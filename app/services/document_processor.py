from collections.abc import Generator
from transformers import AutoTokenizer
import pymupdf4llm
import os
from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.models.vertor_model import VectorEntry


class DocumentProcessor:
    def chunk_tokenize_pdf(
        self,
        pdf_filepath: str,
        tokenizer_name: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> Generator[int, None, None]:

        if not os.filepath.exists(pdf_filepath):
            raise FileNotFoundError()

        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        markdown_file = pymupdf4llm.to_markdown(doc=pdf_filepath, page_chunks=True)

        buffer = []
        mask_buffer = []
        page_buffer = []
        for page in markdown_file:
            page_text = page.get("text", "")
            page_metadata = page.get("metadata", "")

            tokenized_page = tokenizer(page_text)

            for token, mask in tokenized_page:
                buffer.append(token)
                mask_buffer.append(mask)
                page_buffer.append(page_metadata["page_number"])

                if len(buffer) == chunk_size:
                    text_chunk = {
                        "tokenized_text": buffer,
                        "mask": mask,
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
                "mask": mask,
                "page_start": page_buffer[0],
                "page_end": page_buffer[-1],
            }
            yield text_chunk

    def detokenize_text(
        self,
    ):
        pass

    def process_embed_document(self, document_to_process: Document, db: Session):

        if document_to_process.document_type == "pdf":
            for index, text_chunk in self.chunk_tokenize_pdf():
                embedded_text = None  # Load the EmbeddingService
                detokenized_text = self.detokenize_text(text_chunk["tokenized_text"])

                token_chunk_to_write = VectorEntry(
                    document_source_id=document_to_process.id,
                    document_source=document_to_process,
                    page_start=text_chunk["page_start"],
                    page_end=text_chunk["page_end"],
                    chunk_index=index,
                    original_text=detokenized_text,
                    embedding=embedded_text,
                )

            # Write to vector_table possibly in some intelligent manner
