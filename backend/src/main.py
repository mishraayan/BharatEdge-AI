from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import shutil
import os
import logging

from src.models import ChatRequest, ChatResponse, IngestResponse
from src.rag_engine import RAGEngine
from src.ingestion import DocumentIngestor
from src.config import DATA_DIR

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize App
app = FastAPI(title="BharatEdge AI Backend", version="1.0.0")

# CORS (Allow Tauri frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Secure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engines (Lazy loading could be better, but this is simple)
rag_engine = RAGEngine()
ingestor = DocumentIngestor()

@app.get("/health")
def health_check():
    from src.config import LLM_MODEL_PATH
    model_exists = os.path.exists(LLM_MODEL_PATH)
    return {
        "status": "ok", 
        "llm_loaded": rag_engine.llm_engine.llm is not None,
        "model_exists": model_exists
    }

@app.post("/documents/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        # 1. Save File
        filename = file.filename
        file_path = ingestor.save_upload(file.file, filename)
        logger.info(f"File saved to {file_path}")

        # 2. Process (Parse & Chunk)
        chunks, metadatas = ingestor.process_document(file_path)
        
        # 3. Index (Vector DB)
        if chunks:
            rag_engine.vector_db.add_documents(chunks, metadatas)
        
        return IngestResponse(
            filename=filename,
            chunks_count=len(chunks),
            status="indexed"
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
def list_documents():
    """List uploaded documents."""
    try:
        files = os.listdir(DATA_DIR)
        return [{"filename": f} for f in files if os.path.isfile(os.path.join(DATA_DIR, f))]
    except Exception as e:
        return []

@app.delete("/documents/{filename}")
async def delete_document_endpoint(filename: str):
    try:
        # 1. Delete from Disk
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # 2. Delete from Vector DB
        rag_engine.vector_db.delete_document(filename)
        
        return {"status": "deleted", "filename": filename}
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import json

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint providing JSON Events.
    Format:
    - {"type": "citation", "data": [...]}
    - {"type": "token", "data": "text"}
    - {"type": "done"}
    """
    # Get citations first
    citations = rag_engine.get_citations(request.message, sources=request.sources)
    logger.info(f"Query: {request.message} | Filters: {request.sources} | Chunks: {len(citations)}")

    def response_generator():
        try:
            # 1. Yield Citations
            citation_data = [{
                "source": c.source, 
                "page": c.page, 
                "text": c.text[:50] + "..." # Snippet
            } for c in citations]
            
            yield json.dumps({"type": "citation", "data": citation_data}) + "\n"
            
            # 2. Yield Tokens
            for piece in rag_engine.query(request.message, request.history, sources=request.sources):
                if isinstance(piece, dict) and piece.get("type") == "meta":
                     yield json.dumps(piece) + "\n"
                else:
                     yield json.dumps({"type": "token", "data": piece}) + "\n"
                
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(response_generator(), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
