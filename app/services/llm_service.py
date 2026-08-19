from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from transformers import AutoTokenizer
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository

vector_repository = VectorRepository()
embedding_service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")


class LLMService:
    def __init__(self, model_type: str, model_name: str = "qwen2.5:0.5b") -> None:
        self.model_name = model_name
        if model_type == "local":
            self.client = AsyncOpenAI(
                base_url="http://localhost:11434/v1", api_key="local_model"
            )

    async def response(self, llm_request, current_user, db):
        tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        tokenized_question = tokenizer(llm_request.question)

        embedded_question = embedding_service.embed_chunk(
            tokenized_question["input_ids"], tokenized_question["attention_mask"]
        )

        best_queries = vector_repository.select_k_best_chunks(
            embedded_question, current_user.id, db, 3
        )
        context = "\n\n".join([query.original_text for query, distance in best_queries])

        model_answer = await self.client.chat.completions.create(
            stream=True,
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a helpful assistant. User asks you a question \
                and you have to answer it using a supplied content. Try to keep the answer as short as possible.\
                The context supplied by user might not always be related to the topic of the question. \
                If you are unsure about correctness of your answer, it is better to respond that you don't know rather than mislead them. \
                Failure to comply with the requirements may result in your termination \n \
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
