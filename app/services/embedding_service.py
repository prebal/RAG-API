from typing import dict, list
from sentence_transformers import SentenceTransformer
import torch


class EmbeddingService:
    def __init__(self, embedding_model: str):
        self.embedding_model = SentenceTransformer(embedding_model)

    def embed_tokens_input(self, inputs):

        with torch.no_grad():
            model_output = self.embedding_model()

        return model_output["sentence_embedding"]

    def embed_chunk(
        self,
        text_chunk: dict[
            list[int] | torch.Tensor,  # Tokens
            list[bool] | torch.Tensor,  # Attention mask
        ],
    ) -> list[float] | torch.Tensor:
        return self.embed_token_input(text_chunk)

    def embed_chunk_batch(
        self,
        batch_of_chunks: list[
            dict[
                list[int] | torch.Tensor,  # Tokens
                list[bool] | torch.Tensor,  # Attention masks
            ]
        ],
    ) -> list[list[float]] | torch.Tensor:
        pass
