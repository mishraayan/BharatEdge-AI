import os
import fitz  # PyMuPDF
from typing import List, Tuple, Dict
from src.config import DATA_DIR, CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentIngestor:
    def __init__(self):
        # Initialize the splitter with our config
        # Separators prioritize paragraphs, then sentences, then words to keep semantic units intact.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_CHARS,
            chunk_overlap=CHUNK_OVERLAP_CHARS,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            length_function=len,
        )

    def save_upload(self, file_obj, filename: str) -> str:
        """
        Save uploaded file to disk.
        """
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_obj.read())
        return file_path

    def parse_pdf(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from PDF pages with page numbers.
        Returns: List of (text_content, page_number)
        """
        doc = fitz.open(file_path)
        pages_content = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text = " ".join(text.split()).strip()
            
            if text:
                pages_content.append((text, page_num + 1))  # 1-indexed pages
                
        return pages_content

    def process_document(self, file_path: str) -> Tuple[List[str], List[Dict]]:
        """
        End-to-end processing: Parse -> Clean -> Chunk.
        Returns: (chunks, metadatas)
        """
        logger.info(f"Processing document: {file_path}")
        ext = file_path.split('.')[-1].lower()
        raw_pages = []
        
        if ext == 'pdf':
            raw_pages = self.parse_pdf(file_path)
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_pages = [(f.read(), 1)]
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return [], []
        
        all_chunks = []
        all_metadatas = []
        
        filename = os.path.basename(file_path)
        
        for page_text, page_num in raw_pages:
            # Split the text of this page
            page_chunks = self.text_splitter.split_text(page_text)
            
            for chunk in page_chunks:
                all_chunks.append(chunk)
                # Metadata for citation
                all_metadatas.append({
                    "source": filename,
                    "page": page_num,
                    "chunk_len": len(chunk)
                })
        
        logger.info(f"Generated {len(all_chunks)} chunks from {filename}")
        return all_chunks, all_metadatas
