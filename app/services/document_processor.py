from collections.abc import Generator
from transformers import AutoTokenizer
import pymupdf4llm
import os
from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.models.vector_model import VectorEntry
from app.services.embedding_service import EmbeddingService
from app.repositories.vector_repository import VectorRepository

embedding_service = EmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
vector_repository = VectorRepository()


class DocumentProcessor:
    def __init__(self, tokenizer_model_name: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_name)

    def chunk_tokenize_pdf(
        self,
        pdf_filepath: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> Generator[int, None, None]:

        if not os.path.exists(pdf_filepath):
            raise FileNotFoundError()

        markdown_file = pymupdf4llm.to_markdown(doc=pdf_filepath, page_chunks=True)

        buffer = []
        mask_buffer = []
        page_buffer = []

        for page in markdown_file:
            page_text = page.get("text", "")
            page_metadata = page.get("metadata", "")

            tokenized_page = self.tokenizer(page_text)

            for token, mask in zip(
                tokenized_page["input_ids"], tokenized_page["attention_mask"]
            ):
                buffer.append(token)
                mask_buffer.append(mask)
                page_buffer.append(page_metadata["page_number"])

                if len(buffer) == chunk_size:
                    text_chunk = {
                        "tokenized_text": buffer,
                        "mask": mask_buffer,
                        "page_start": page_buffer[0],
                        "page_end": page_buffer[-1],
                    }
                    yield text_chunk

                    buffer = buffer[-chunk_overlap:]
                    mask_buffer = mask_buffer[-chunk_overlap:]
                    page_buffer = page_buffer[-chunk_overlap:]

        if buffer:
            text_chunk = {
                "tokenized_text": buffer,
                "mask": mask_buffer,
                "page_start": page_buffer[0],
                "page_end": page_buffer[-1],
            }
            yield text_chunk

    def process_embed_document(self, document_to_process: Document, db: Session):

        if document_to_process.document_type == "pdf":
            embedding_entries_to_write_into_db = []
            for index, text_chunk in enumerate(
                self.chunk_tokenize_pdf(
                    document_to_process.filepath,
                    256,
                    30,
                )
            ):
                print(text_chunk)
                embedded_text = embedding_service.embed_chunk(
                    text_chunk["tokenized_text"], text_chunk["mask"]
                )  # Load the EmbeddingService
                detokenized_text = self.tokenizer.decode(
                    text_chunk["tokenized_text"], skip_special_tokens=True
                )

                token_chunk_to_write = VectorEntry(
                    document_source_id=document_to_process.id,
                    document_source=document_to_process,
                    page_start=text_chunk["page_start"],
                    page_end=text_chunk["page_end"],
                    chunk_index=index,
                    original_text=detokenized_text,
                    embedding=embedded_text,
                )

                embedding_entries_to_write_into_db.append(token_chunk_to_write)

        vector_repository.create_vector(embedding_entries_to_write_into_db, db)

        # Write to vector_table possibly in some intelligent manner
