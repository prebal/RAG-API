from typing import List, Dict
import torch
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import CrossEncoder


class ModelService:
    def __init__(
        self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> None:
        self.embedding_model = AutoModel.from_pretrained(embedding_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def embed_tokens_input(
        self, inputs: torch.Tensor, mask: torch.Tensor
    ) -> List[float]:

        with torch.no_grad():
            model_output = self.embedding_model(
                torch.as_tensor(inputs).reshape(1, -1),
                torch.as_tensor(mask).reshape(1, -1),
            )

        embeddings = model_output.last_hidden_state
        mask = torch.as_tensor(mask).unsqueeze(-1).float()
        pooled_embedding = (embeddings * mask).sum(dim=1) / mask.sum(dim=0)
        return pooled_embedding.detach().reshape(-1).tolist()

    def embed_chunk(self, tokens: torch.Tensor, mask: torch.Tensor) -> List[float]:
        return self.embed_tokens_input(tokens, mask)

    def rerank_chunks(
        self, query: str, original_text_chunk_list: List[str], top_k: int = 5
    ) -> List[Dict[str, int | float | str]]:
        return self.cross_encoder.rank(
            query, original_text_chunk_list, return_documents=True, top_k=top_k
        )
