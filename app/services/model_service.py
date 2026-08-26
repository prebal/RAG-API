from typing import list, dict, Literal
import torch
from transformers import AutoModel, AutoTokenizer
from sentence-transformers import CrossEncoder


class ModelService:
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.embedding_model = AutoModel.from_pretrained(embedding_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)
        self.cross_encoder = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def embed_tokens_input(self, inputs: list[int] , mask: list[int]) -> list[float]:

        with torch.no_grad():
            model_output = self.embedding_model(
                torch.as_tensor(inputs).reshape(1, -1),
                torch.as_tensor(mask).reshape(1, -1),
            )

        embeddings = model_output.last_hidden_state
        mask = torch.as_tensor(mask).unsqueeze(-1).float()
        pooled_embedding = (embeddings * mask).sum(dim=1) / mask.sum(dim=0)
        return pooled_embedding.detach().reshape(-1).tolist()

    def embed_chunk(
        self, tokens: list[int], mask: list[int]
    ) -> list[float]:
        return self.embed_tokens_input(tokens, mask)

    def rerank_chunks(self, query: str, original_text_chunk_list: list[str], top_k: int = 5) -> list[dict[Literal[“corpus_id”, “score”, “text”], int | float | str]]]:
        return self.cross_encoder.rank(query, original_text_chunk_list, return_documents = True, top_k = top_k)
      
        
