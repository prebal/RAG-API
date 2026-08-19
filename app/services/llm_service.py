from openai import OpenAI
from transformers import AutoTokenizer
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository

vector_repository = VectorRepository()
embedding_service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")

class LLMService:
    def __init__(self, model_type: str, model_name: str = "qwen2.5:0.5b") -> None:
        self.model_name = model_name
        if model_type == "local":
            self.client = OpenAI(base_url = "http://localhost:11434/v1", api_key = "local_model")

    def response(self, llm_request, current_user, db):
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        tokenized_question = tokenizer(llm_request.question)
 
        embedded_question = embedding_service.embed_chunk(tokenized_question["input_ids"], tokenized_question["attention_mask"])

        best_queries = vector_repository.select_k_best_chunks(embedded_question, current_user.id, db, 3)
        context = "\n\n".join([query.original_text for query, distance in best_queries])
        print(context)

        model_answer = self.client.chat.completions.create(
            model = self.model_name,
            messages = [{
                "role": "user",
                "content": f"You are a helpful assistant. User asks you a question \
                and you have to answer it using a supplied content. Try to keep the answer as short as possible.\
                The context supplied by user might not always be related to the topic of the question. \
                If you are unsure about correctness of your answer, it is better to respond that you don't know \n \
                Users question: {llm_request.question} \
                Context:{context}"
            }]

        )
        print(context)
        answer = model_answer.choices[0].message.content
        return answer
