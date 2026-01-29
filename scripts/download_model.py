import os
from sentence_transformers import SentenceTransformer

# Target Directory
# backend/models/embeddings/all-MiniLM-L6-v2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "backend", "models", "embeddings", "all-MiniLM-L6-v2")

print(f"Downloading 'all-MiniLM-L6-v2' to: {TARGET_DIR}")

# This will download the full model structure (including submodules) correctly
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model.save(TARGET_DIR)

print("\nSUCCESS: Model saved. You can now go offline.")
