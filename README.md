# BharatEdge AI 🇮🇳

**Offline-First, Privacy-Centric RAG for Every Laptop.**

BharatEdge AI is an open-source tool built to bring high-performance Document Q&A to standard hardware (8GB RAM, i3/i5/i7 CPUs) commonly found in Indian homes, schools, and small businesses. It runs **100% offline** with zero external API calls.

---

## ✨ Features (V1.4 Standard)
*   **Privacy First**: Your documents never leave your machine. No cloud, no tracking.
*   **Edge Inference**: Optimized LLM execution using `llama-cpp-python` (Quantized GGUF).
*   **Grounded RAG**: Strictly uses your indexed PDF/Text files for answers with full citations.
*   **Multi-Lingual**: Native support for **English** and **Bengali (বাংলা)**.
*   **Zero-Config Vector DB**: Automatic local persistence using ChromaDB.

## 🚀 Getting Started

### 📥 Download & Install (For Users)
If you are not a developer and just want to use the app:
1.  Go to the **[Releases](https://github.com/mishraayan/BharatEdge-AI/releases)** page.
2.  Download the latest installer (`.msi` for traditional installation or `.exe` for portable/standalone).
3.  Run the installer and follow the prompts.
4.  *Note: On your first run, the app will download the necessary AI models (~2GB). Ensure you have a stable connection for the initial setup.*

---

### 💻 Developer Setup

1.  **Clone & Enter**
    ```bash
    git clone https://github.com/ayanmishra/BharatEdge-AI.git
    cd BharatEdge-AI
    ```

2.  **Initialize Environment**
    ```bash
    scripts\setup_dev_env.bat
    ```

3.  **Fetch AI Models**
    ```bash
    # Download 3B Parameter LLM (~2.2GB)
    python scripts/download_llm.py
    
    # Download Local Embedding Weights
    python scripts/download_model.py
    ```

4.  **Start Services**
    ```bash
    # Terminal 1: Backend
    scripts\start_backend.bat
    
    # Terminal 2: Frontend
    cd app
    npm install
    npm run tauri dev
    ```

## 🛠️ Technical Specs
- **Frontend**: Tauri v2, React 18, Tailwind CSS (Glassmorphism UI)
- **Backend Core**: Python 3.11, FastAPI
- **LLM Engine**: Qwen-2.5-3B (4-bit quantization)
- **Vector Base**: ChromaDB
- **Parsing**: PyMuPDF (Optimized for fast local parsing)

## 🗺️ Roadmap
- [x] Phase 1: Optimized CPU Inference
- [x] Phase 2: Standalone Windows Packaging
- [ ] Phase 3: Hindi & Regional Language Fine-tuning
- [ ] Phase 4: Integrated OCR Support (Coming in future releases)

## 🤝 Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. Please read [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
**BharatEdge AI** - *Empowering the edge with intelligence.* 🇮🇳
