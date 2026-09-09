import asyncio
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.repositories.vector_repository import VectorRepository
from app.services.model_service import ModelService


class LLMService:
    def __init__(
        self,
        vector_repository: VectorRepository,
        model_service: ModelService,
        client: AsyncOpenAI,
        model_name: str = "qwen2.5:0.5b",
    ) -> None:
        self.vector_repository = vector_repository
        self.model_service = model_service
        self.model_name = model_name
        self.client = client

    async def response(self, llm_request, current_user) -> AsyncGenerator[str]:
        tokenized_question = self.model_service.tokenizer(llm_request.question)

        embedded_question = await asyncio.to_thread(
            self.model_service.embed_chunk,
            tokenized_question["input_ids"],
            tokenized_question["attention_mask"],
        )

        best_queries = await self.vector_repository.select_k_best_chunks(
            embedded_question, current_user.id, 20
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

        model_answer = await self.client.chat.completions.create(
            stream=True,
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a helpful assistant. User asks you a question \
                and you have to answer it using a supplied content. Try to keep the answer as short as possible.\
                The context supplied by user might not always be related to the topic of the question. \
                If you are unsure about correctness of your answer, it is better to respond that you don't know rather than mislead them. \n \
                Users question: {llm_request.question} \
                Context:{context}",
                }
            ],
        )
        # Curiously ollama fails to AsyncStream
        if isinstance(model_answer, ChatCompletion):
            non_async_content = model_answer.choices[0].message.content
            if non_async_content:
                yield f"data: {non_async_content}\n\n"
        else:
            async for stream_chunk in model_answer:
                text_to_stream = stream_chunk.choices[0].delta.content

                if text_to_stream:
                    yield f"data: {text_to_stream}\n\n"
