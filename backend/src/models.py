from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = [] # List of {"role": "user/assistant", "content": "..."}
    sources: Optional[List[str]] = None # Optional list of specific filenames to filter by

class DocumentChunk(BaseModel):
    text: str
    source: str
    page: int
    score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[DocumentChunk]

class IngestResponse(BaseModel):
    filename: str
    chunks_count: int
    status: str
