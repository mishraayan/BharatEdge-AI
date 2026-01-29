# Manual Testing Guide for BharatEdge AI

Follow these steps to run the "BharatEdge AI" V1 Prototype on your local machine.

## 1. Environment Setup

### Prerequisites
*   **Python 3.10+**: Ensure `python` is in your PATH.
*   **Node.js 18+**: For the frontend.
*   **Rust**: Required for Tauri. Install from [rustup.rs](https://rustup.rs/) if missing.
*   **C++ Build Tools**: Required for `llama-cpp-python`. If `pip install` fails later, you likely need [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Select "Desktop development with C++").

### Automated Setup Script
Run the helper script to create the Python environment and install dependencies:
```cmd
scripts\setup_dev_env.bat
```

---

## 2. Download Models (Critical Step)
Since this is an offline AI, you must manually place the model files.

1.  **LLM (GGUF)**:
    *   Download **Qwen2.5-3B-Instruct-Q4_K_M.gguf**.
    *   **Link**: [HuggingFace - Qwen2.5-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf?download=true)
    *   **Action**: Ensure it is named exactly `qwen2.5-3b-instruct-q4_k_m.gguf` (matching `config.py`).
    *   **Move to**: `BharatEdge-AI\backend\models\`

2.  **Embeddings (Required for RAG)**:
    *   **Action**: BharatEdge AI is designed to run fully offline. Therefore, the embedding model must be downloaded once and placed locally.
    *   **Download**: `all-MiniLM-L6-v2` from [HuggingFace](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/main).
    *   **Structure**: Create folder `backend/models/embeddings/all-MiniLM-L6-v2/` and place the files there (config.json, pytorch_model.bin, tokenizer.json, etc.).
    *   **Note**: You can clone the repo: `git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 backend/models/embeddings/all-MiniLM-L6-v2`

---

## 3. Running the App (Two Terminals)

### Terminal 1: Backend (Brain)
```cmd
cd backend
venv\Scripts\activate
python -m src.main
```
*Wait until you see: `Application startup complete`*

### Terminal 2: Frontend (UI)
```cmd
cd app
npm run tauri dev
```
*This will launch the Desktop Window.*

---

## 4. Test Scenario Checklist

1.  **Health Check**:
    *   [ ] Does the app launch?
    *   [ ] Does the "Starting AI Engine..." splash screen disappear automatically?
    *   [ ] Is the Status Bar showing "Ready"?

2.  **Document Ingestion**:
    *   [ ] Click top-left Upload area (or Drop a PDF).
    *   [ ] Watch for "Processing..." indicator.
    *   [ ] Does the file appear in the "Documents" list?

3.  **Chat & RAG**:
    *   [ ] Type: *"What is the summary of the document?"*
    *   [ ] **Check 1**: Does text stream in? (Not one big block).
    *   [ ] **Check 2**: Are there Citations chips like `[report.pdf | p.1]`?
    *   [ ] **Check 3**: Click a citation chip. Does it show the source name?

4.  **Performance (Monitor Task Manager)**:
    *   [ ] **RAM**: Check `python.exe` memory usage. Should be < 3GB.
    *   [ ] **CPU**: Check usage during answer generation.

## Troubleshooting
*   **"Model not found"**: Check `backend/models/` for the exact filename `qwen2.5-3b-instruct-q4_k_m.gguf`.
*   **"Backend Connection Failed"**: Ensure Terminal 1 is running and didn't crash.
*   **Build Errors**: If `npm run tauri dev` fails, ensure Rust is installed.
