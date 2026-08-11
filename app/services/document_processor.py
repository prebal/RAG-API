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
        
        for page in markdown_file:
            page_text = page.get("text", "")
            page_metadata = page.get("metadata", "")

            tokenized_page = tokenizer(page_text)

            

            while 
