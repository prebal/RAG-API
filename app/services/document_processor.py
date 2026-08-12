from collections.abc import Generator
from transformers import AutoTokenizer
import pymupdf4llm
import os

class DocumentProcessor:
    def chunk_tokenize_pdf(
        self, 
        pdf_filepath: str, 
        tokenizer_name: str, 
        chunk_size: int,
        chunk_overlap: int
        ) -> Generator[int, None, None]:

        if not os.filepath.exists(pdf_filepath):
            raise FileNotFoundError()
       
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        markdown_file = pymupdf4llm.to_markdown(doc = pdf_filepath, page_chunks = True)
        
        buffer = []
        for page in markdown_file:
            page_text = page.get("text", "")
            page_metadata = page.get("metadata", "")

            tokenized_page = tokenizer(page_text).get(input_ids)

            n_tokens_on_page = len(tokenized_page)

            for token in tokenized_page:
                buffer.append(token)
                if len(buffer) == chunk_size:
                    yield buffer

                    buffer = buffer[-chunk_overlap:]

        if buffer:
            yield buffer

    def process_embed_document(self, ):
