import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import HTTPException
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.models.auth_model import User
from app.models.message_model import Message
from app.models.notebook_model import Notebook
from app.repositories.messages_repository import MessageRepository
from app.repositories.notebook_repository import NotebookRepository
from app.repositories.vector_repository import VectorRepository
from app.schemas.llm_schema import LLMRequest, GetChatHistoryRequest
from app.services.model_service import ModelService

service_logger = logging.getLogger("app")


class LLMService:
    def __init__(
        self,
        vector_repository: VectorRepository,
        model_service: ModelService,
        message_repository: MessageRepository,
        notebook_repository: NotebookRepository,
        client: AsyncOpenAI,
        model_name: str = "qwen2.5:0.5b",
    ) -> None:
        self.vector_repository = vector_repository
        self.model_service = model_service
        self.message_repository = message_repository
        self.notebook_repository = notebook_repository
        self.model_name = model_name
        self.client = client

    async def prepare_prompt(
        self, llm_request: LLMRequest, current_user: User
    ) -> tuple[str, str, str, Notebook]:
        # Validate the notebook first so a 400 never pays for embedding/vector work.
        queried_notebook = await self.notebook_repository.get_notebook_by_name(
            llm_request.notebook_name, current_user.id
        )
        if queried_notebook is None:
            raise HTTPException(
                400,
                detail="The notebook doesn't exist or you don't have the authorization to use it",
            )

        notebook_id = queried_notebook.id

        tokenized_question = self.model_service.tokenizer(llm_request.question)

        embedded_question = await asyncio.to_thread(
            self.model_service.embed_chunk,
            tokenized_question["input_ids"],
            tokenized_question["attention_mask"],
        )

        best_queries = await self.vector_repository.select_k_best_chunks(
            embedded_question, current_user.id, notebook_id, 20
        )

        if len(best_queries) <= 5:
            context = "\n\n".join(
                [
                    query.original_text
                    for query, distance in best_queries
                    if distance < 0.5
                ]
            )
        else:
            original_text_chunk_list = [
                query.original_text for query, _ in best_queries
            ]
            reranker_result = await asyncio.to_thread(
                self.model_service.rerank_chunks,
                llm_request.question,
                original_text_chunk_list,
                top_k=5,
            )
            context = "\n\n".join(
                [reranked_chunk["text"] for reranked_chunk in reranker_result]
            )

        conversation_history_rows = (
            await self.message_repository.get_all_messages_by_notebook_id(
                notebook_id, current_user.id
            )
        )

        if conversation_history_rows:
            conversation_history = "\n\n".join(
                f"{message.role}: {message.content}"
                for message in conversation_history_rows
            )
        else:
            conversation_history = ""

        # Persist the user message only after the history snapshot was taken,
        # so the current question is not echoed inside its own prompt history.
        new_message = Message(
            notebook_assigned_id=notebook_id,
            notebook_assigned=queried_notebook,
            message_owner_id=current_user.id,
            message_owner=current_user,
            role="user",
            content=str(llm_request.question),
            created_at=datetime.now(UTC),
        )

        await self.message_repository.create_message(new_message)

        # Return order matches the unpacking in generate_response.
        return (llm_request.question, conversation_history, context, queried_notebook)

    async def generate_response(
        self, llm_request: LLMRequest, current_user: User
    ) -> AsyncGenerator:
        service_logger.info(
            f"LLMService.generate_response: username={current_user.username}, "
            f"notebook_name={llm_request.notebook_name}"
        )

        (
            question,
            conversation_history,
            context,
            queried_notebook,
        ) = await self.prepare_prompt(llm_request, current_user)

        model_answer = await self.client.chat.completions.create(
            stream=True,
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a helpful assistant. User asks you a question \
                and you have to answer it using a supplied content. Try to keep the answer as short as possible.\
                The context supplied by user might not always be related to the topic of the question. You might recieve additional context via conversation history. \
                If you are unsure about correctness of your answer, it is better to respond that you don't know rather than mislead them. \n \
                If you recieve empty context, state that there is not enough information \
                Conversation_history: {conversation_history} \
                Users question: {question} \
                Context: {context}",
                }
            ],
        )
        response_chunks = []

        # Curiously ollama sometimes fails to AsyncStream
        if isinstance(model_answer, ChatCompletion):
            non_async_content = model_answer.choices[0].message.content
            if non_async_content:
                response_chunks.append(non_async_content)
                yield f"data: {non_async_content}\n\n"
        else:
            async for stream_chunk in model_answer:
                text_to_stream = stream_chunk.choices[0].delta.content
                if text_to_stream:
                    response_chunks.append(text_to_stream)
                    yield f"data: {text_to_stream}\n\n"

        new_message = Message(
            notebook_assigned_id=queried_notebook.id,
            message_owner_id=current_user.id,
            message_owner=current_user,
            role="assistant",
            content="".join(response_chunks),
            created_at=datetime.now(UTC),
        )

        await self.message_repository.create_message(new_message)

    async def get_chat_history(
        self, chat_history_request: GetChatHistoryRequest, current_user: User
    ) -> list[dict[str, str]]:
        if chat_history_request.history_start > chat_history_request.history_end:
            raise HTTPException(
                422,
                detail="The range for subselecting messages for this chat history is invalid.",
            )

        queried_notebook = await self.notebook_repository.get_notebook_by_name(
            chat_history_request.notebook_name, current_user.id
        )
        if queried_notebook is None:
            raise HTTPException(
                400,
                detail="The notebook doesn't exist or you don't have the authorization to use it",
            )

        subselected_message_entries = (
            await self.message_repository.get_all_messages_by_notebook_id(
                queried_notebook.id, current_user.id, chat_history_request.history_end
            )
        )[chat_history_request.history_start :]
        return [
            {message_entry[0]: message_entry[1]}
            for message_entry in subselected_message_entries
        ]
