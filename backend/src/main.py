from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import shutil
import os
import sys
import logging

from src.models import ChatRequest, ChatResponse, IngestResponse
from src.rag_engine import RAGEngine
from src.ingestion import DocumentIngestor
from src.config import DATA_DIR, LOG_FILE

# Initialize Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
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

# Global Engines (Lazy loading to prevent startup crashes)
_rag_engine = None
_ingestor = None
download_progress = {"status": "idle", "progress": 0, "message": ""}

def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        try:
            _rag_engine = RAGEngine()
        except Exception as e:
            logger.error(f"Failed to initialize RAGEngine: {e}")
    return _rag_engine

def get_ingestor():
    global _ingestor
    if _ingestor is None:
        try:
            _ingestor = DocumentIngestor()
        except Exception as e:
            logger.error(f"Failed to initialize DocumentIngestor: {e}")
    return _ingestor

@app.get("/setup/status")
def get_setup_status():
    return download_progress

@app.post("/setup/init")
async def init_setup(background_tasks: BackgroundTasks):
    if download_progress["status"] == "downloading":
        return {"message": "Download already in progress"}
    
    background_tasks.add_task(run_setup_tasks)
    return {"message": "Setup started"}

def run_setup_tasks():
    global download_progress
    from src.config import LLM_MODEL_PATH, LLM_MODEL_FILENAME, MODELS_DIR
    import requests
    
    try:
        download_progress["status"] = "downloading"
        
        # 1. Download LLM
        # 1. Download LLM
        min_size = 1.5 * 1024 * 1024 * 1024 # 1.5 GB
        
        if os.path.exists(LLM_MODEL_PATH):
            file_size = os.path.getsize(LLM_MODEL_PATH)
            if file_size < min_size:
                logger.warning(f"Model file corrupt (size {file_size} < {min_size}). Deleting...")
                try:
                    os.remove(LLM_MODEL_PATH)
                except Exception as e:
                    logger.error(f"Failed to delete corrupt model: {e}")
        
        if not os.path.exists(LLM_MODEL_PATH):
            url = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
            logger.info(f"Downloading LLM from {url}...")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            download_progress["message"] = "Downloading LLM Brain (2.5GB)..."
            
            with open(LLM_MODEL_PATH, 'wb') as f:
                downloaded = 0
                for data in response.iter_content(chunk_size=1024*1024): # 1MB chunks
                    downloaded += len(data)
                    f.write(data)
                    if total_size > 0:
                        download_progress["progress"] = int((downloaded / total_size) * 80) # 80% for LLM
        
        # 2. Embedding Model
        download_progress["message"] = "Downloading Embedding Model..."
        from src.config import EMBEDDING_CACHE_DIR, EMBEDDING_MODEL_NAME
        
        # Check if model exists (heuristic: check for config.json)
        if not os.path.exists(os.path.join(EMBEDDING_MODEL_NAME, "config.json")):
             logger.info(f"Downloading embedding model to {EMBEDDING_MODEL_NAME}...")
             from sentence_transformers import SentenceTransformer
             
             # Download and save to ensuring persistence in the correct path
             model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=EMBEDDING_CACHE_DIR)
             model.save(EMBEDDING_MODEL_NAME)

        download_progress["message"] = "Initializing Embedding Engine..."
        download_progress["progress"] = 90
        get_rag_engine() # This will trigger model loads
        
        download_progress["status"] = "complete"
        download_progress["progress"] = 100
        download_progress["message"] = "Ready to Go!"
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        download_progress["status"] = "error"
        download_progress["message"] = str(e)

@app.get("/health")
def health_check():
    from src.config import LLM_MODEL_PATH, EMBEDDING_MODEL_NAME
    
    min_size = 1.5 * 1024 * 1024 * 1024 # 1.5 GB
    llm_exists = os.path.exists(LLM_MODEL_PATH) and os.path.getsize(LLM_MODEL_PATH) > min_size
    embedding_exists = os.path.exists(os.path.join(EMBEDDING_MODEL_NAME, "config.json"))
    
    engine = get_rag_engine()
    return {
        "status": "ok", 
        "llm_loaded": engine.llm_engine.llm is not None if engine and engine.llm_engine else False,
        "model_exists": llm_exists and embedding_exists,
        "engine_ready": engine is not None
    }

@app.post("/documents/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    ingestor = get_ingestor()
    if not ingestor:
        raise HTTPException(status_code=503, detail="Ingestion engine not ready. Check model files.")
    
    try:
        # 1. Save File
        filename = file.filename
        file_path = ingestor.save_upload(file.file, filename)
        logger.info(f"File saved to {file_path}")

        # 2. Process (Parse & Chunk)
        chunks, metadatas = ingestor.process_document(file_path)
        
        # 3. Index (Vector DB)
        if chunks:
            engine = get_rag_engine()
            if engine:
                engine.vector_db.add_documents(chunks, metadatas)
        
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
        engine = get_rag_engine()
        if engine:
            engine.vector_db.delete_document(filename)
        
        return {"status": "deleted", "filename": filename}
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import json

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint providing JSON Events.
    """
    engine = get_rag_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="AI Engine not ready. Check model files.")

    # Get citations first
    citations = engine.get_citations(request.message, sources=request.sources)
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
            for piece in engine.query(request.message, request.history, sources=request.sources):
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
    # Use the app object directly instead of a string for sidecar reliability
    uvicorn.run(app, host="127.0.0.1", port=8000)
