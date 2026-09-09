import os
from collections.abc import Generator
from typing import Any, Dict, List

import pymupdf4llm

from app.models.document_model import Document
from app.models.vector_model import VectorEntry
from app.repositories.vector_repository import VectorRepository
from app.services.model_service import ModelService


class DocumentProcessor:
    def __init__(
        self, model_service: ModelService, vector_repository: VectorRepository
    ) -> None:
        self.model_service = model_service
        self.vector_repository = vector_repository

    def chunk_tokenize_pdf(
        self,
        pdf_filepath: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> Generator[dict[str, Any]]:

        if not os.path.exists(pdf_filepath):
            raise FileNotFoundError()

        markdown_file = pymupdf4llm.to_markdown(doc=pdf_filepath, page_chunks=True)

        text_buffer = []
        mask_buffer = []
        page_buffer = []

        for page in markdown_file:
            page_text = page.get("text", "")
            page_metadata = page.get("metadata", "")

            tokenized_page = self.model_service.tokenizer(page_text)

            for token, mask in zip(
                tokenized_page["input_ids"], tokenized_page["attention_mask"]
            ):
                text_buffer.append(token)
                mask_buffer.append(mask)
                page_buffer.append(page_metadata["page_number"])

                if len(text_buffer) == chunk_size:
                    yield {
                        "tokenized_text": text_buffer,
                        "mask": mask_buffer,
                        "page_start": page_buffer[0],
                        "page_end": page_buffer[-1],
                    }

                    text_buffer = text_buffer[-chunk_overlap:]
                    mask_buffer = mask_buffer[-chunk_overlap:]
                    page_buffer = page_buffer[-chunk_overlap:]

        if text_buffer:
            yield {
                "tokenized_text": text_buffer,
                "mask": mask_buffer,
                "page_start": page_buffer[0],
                "page_end": page_buffer[-1],
            }

    def chunk_tokenize_txt(
        self, txt_filepath: str, chunk_size: int, chunk_overlap: int
    ) -> Generator[Dict[str, Any]]:

        if not os.path.exists(txt_filepath):
            raise FileNotFoundError()

        with open(file=txt_filepath, encoding="utf-8", mode="r") as txt_file:
            txt_file_content = txt_file.readlines()

        text_buffer = []
        mask_buffer = []
        line_buffer = []

        for line_index, line in enumerate(txt_file_content):
            tokenized_line = self.model_service.tokenizer(line)
            for token, mask in zip(
                tokenized_line["input_ids"], tokenized_line["attention_mask"]
            ):
                text_buffer.append(token)
                mask_buffer.append(mask)
                line_buffer.append(line_index)

                if len(text_buffer) == chunk_size:
                    yield {
                        "tokenized_text": text_buffer,
                        "mask": mask_buffer,
                        "page_start": line_buffer[0],
                        "page_end": line_buffer[-1],
                    }

                    text_buffer = text_buffer[-chunk_overlap:]
                    mask_buffer = mask_buffer[-chunk_overlap:]
                    line_buffer = line_buffer[-chunk_overlap:]

        if text_buffer:
            yield {
                "tokenized_text": text_buffer,
                "mask": mask_buffer,
                "page_start": line_buffer[0],
                "page_end": line_buffer[-1],
            }

    def embed_document(
        self, document_to_process: Document
    ) -> List[Dict[str, int | str]]:
        chunks = []
        if document_to_process.document_type == "pdf":
            chunk_generator = self.chunk_tokenize_pdf(
                document_to_process.filepath, 256, 30
            )
        elif document_to_process.document_type == "txt":
            chunk_generator = self.chunk_tokenize_txt(
                document_to_process.filepath, 256, 30
            )
        else:
            raise NotImplementedError

        for chunk_index, text_chunk in enumerate(chunk_generator):
            embedded_text = self.model_service.embed_chunk(
                text_chunk["tokenized_text"], text_chunk["mask"]
            )

            detokenized_text = self.model_service.tokenizer.decode(
                text_chunk["tokenized_text"], skip_special_tokens=True
            )

            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "page_start": text_chunk["page_start"],
                    "page_end": text_chunk["page_end"],
                    "original_text": detokenized_text,
                    "embedded_text": embedded_text,
                }
            )

        return chunks

    async def persist_chunks(
        self, document_to_process: Document, chunks_with_embedding: list[dict]
    ) -> None:
        embedding_entries_to_write_into_db = []
        for text_chunk in chunks_with_embedding:
            token_chunk_to_write = VectorEntry(
                document_source_id=document_to_process.id,
                document_source=document_to_process,
                page_start=text_chunk["page_start"],
                page_end=text_chunk["page_end"],
                chunk_index=text_chunk["chunk_index"],
                original_text=text_chunk["original_text"],
                embedding=text_chunk["embedded_text"],
            )

            embedding_entries_to_write_into_db.append(token_chunk_to_write)

        await self.vector_repository.create_vector(embedding_entries_to_write_into_db)
