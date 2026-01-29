import os

import sys

# Base Directories
if getattr(sys, 'frozen', False):
    # If running as an installed app, use User Home to avoid Program Files permission errors
    # This creates a folder like C:\Users\Name\BharatEdge-AI-Data
    HOME_DIR = os.path.expanduser("~")
    BACKEND_DIR = os.path.join(HOME_DIR, ".bharatedge")
else:
    # If running normally (source)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.dirname(BASE_DIR)


DATA_DIR = os.path.join(BACKEND_DIR, "data")
DB_DIR = os.path.join(BACKEND_DIR, "database")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")

# Hardware Configuration (8GB RAM Target)
# n_ctx: Context window (limited to saving RAM on low-spec units)
MAX_CONTEXT_WINDOW = 4096 

# n_threads Detection
import multiprocessing
def get_optimal_threads():
    try:
        cores = multiprocessing.cpu_count()
        # For 4 cores, use 4. For more, use cores-1 to keep system responsive.
        return max(1, cores if cores <= 4 else cores - 1)
    except:
        return 4

CPU_THREADS = get_optimal_threads()

# GPU Configuration (Optional)
# To use GPU, you must install llama-cpp-python with CUDA support:
# CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir
USE_GPU = os.getenv("BHARATEDGE_GPU", "false").lower() == "true"
# -1 means offload all layers to GPU (Best for accuracy and speed if VRAM permits)
# For 3B models, ~35-40 layers is typical.
N_GPU_LAYERS = 35 if USE_GPU else 0 

# Model Paths
# User must place these models here manually or via script
LLM_MODEL_FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
LLM_MODEL_PATH = os.path.join(MODELS_DIR, LLM_MODEL_FILENAME)

# Embedding Model - Offline Configuration
# User must download 'all-MiniLM-L6-v2' and place it in backend/models/embeddings/all-MiniLM-L6-v2
# IMPORTANT: Convert to absolute path to ensure SentenceTransformer treats it as a folder, not a repo_id
EMBEDDING_MODEL_NAME = os.path.abspath(os.path.join(MODELS_DIR, "embeddings", "all-MiniLM-L6-v2"))
# Ensure the directory structure exists in code (or user creates it)
EMBEDDING_CACHE_DIR = os.path.join(MODELS_DIR, "embeddings")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
# We Create the embedding folder too so user sees it
os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)

# --- RAG Settings ---
# Chunking Strategy
# Rationale: ~400-500 words (approx 1500-2000 chars) is a good balance for capturing 
# semantic meaning while keeping granularity high for retrieval.
CHUNK_SIZE_CHARS = 1000 
CHUNK_OVERLAP_CHARS = 200

# Context Budget
# Phi-3 / Qwen context window is typically 4096 tokens.
# We reserve space for system prompt, user query, and generation.
# Target ~2000 tokens for retrieved context to leave room for the rest.
MAX_RETRIEVAL_TOKENS = 2500
TOP_K_RETRIEVAL = 20  # Increased further to ensure secondary documents are not crowded out

# LLM Generation Settings
LLM_TEMPERATURE = 0.1       # Low temperature for factual RAG
LLM_MAX_TOKENS = 512        # Max new tokens to generate
LLM_CONTEXT_WINDOW = 4096   # Total context window of the model

