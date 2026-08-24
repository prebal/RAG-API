from typing import Dict, List
from transformers import AutoModel, AutoTokenizer
import torch


class ModelService:
    def __init__(self, embedding_model_name: str):
        self.embedding_model = AutoModel.from_pretrained(embedding_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)

    def embed_tokens_input(self, inputs, mask):

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
        self, tokens: list[int], mask: List[int]
    ) -> list[float] | torch.Tensor:
        return self.embed_tokens_input(tokens, mask)
