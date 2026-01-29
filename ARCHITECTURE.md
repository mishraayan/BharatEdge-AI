# Architecture Design

BharatEdge AI follows a **Sidecar Architecture** pattern to combine a lightweight, native GUI (Tauri) with a robust Python AI backend.

## System Overview

```mermaid
graph TD
    User[End User] -->|Interacts| UI[Tauri GUI (React)]
    
    subgraph "Local Device (Offline)"
        UI -- HTTP REST --> Backend[Python Backend (FastAPI)]
        
        Backend --> Orchestrator[RAG Orchestrator]
        
        Orchestrator -->|1. Parse & Chunk| Ingest[Ingestion Engine]
        Ingest -->|PDF/Txt| Docs[User Files]
        
        Orchestrator -->|2. Vector Search| VDB[(ChromaDB)]
        VDB <-->|Embed| EmbedModel[all-MiniLM-L6-v2]
        
        Orchestrator -->|3. Inference| LLM[LLM Engine (llama.cpp)]
        LLM -->|Load| ModelFile[GGUF Model (Phi-3 / Qwen)]
    end
```

## Key Components

### 1. Frontend (Tauri)
*   **Role**: User Interface, File Selection, Response Display.
*   **Why Tauri?**: Uses the system webview (Edge/WebView2 on Windows) instead of bundling Chrome (Electron), saving ~200MB RAM.
*   **Communication**: HTTP calls to `localhost:8000`. Tauri manages the lifecycle of the Python backend process.

### 2. Backend (Python/FastAPI)
*   **Role**: The brain. Handles all AI logic.
*   **Isolation**: Runs as a subprocess. Can be replaced transparently.
*   **API**: Exposes `/chat` (Streaming) and `/upload` (Processing).

### 3. RAG Pipeline
*   **Ingestion**: `RecursiveCharacterTextSplitter` chunks documents (~1000 chars).
*   **Storage**: ChromaDB (Persisted to disk in `%AppData%` or local folder).
*   **Retrieval**: Fetches top 5 semantic matches.
*   **Generation**: Constructs a strict prompt with citations `[1]` and streams output.

## Limits & Constraints
*   **RAM**: We respect a hard 4GB Limit for the entire AI subsystem (Model + Embeddings + VectorDB) to ensure the OS remains responsive on 8GB machines.
*   **Context Window**: 4096 Tokens max. We allocate ~2500 for retrieved context.

## Deployment Strategy
*   **Distribution**: One-click `.exe` installer.
*   **Runtime**: Embeddable Python 3.10 is shipped with the app. No `pip install` required for end-users.
