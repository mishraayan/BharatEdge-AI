import os
import sys
from sentence_transformers import SentenceTransformer

# 1. Use RELATIVE path to avoid HuggingFace validation issues with Windows paths
DATA_DIR = "./models/embeddings/all-MiniLM-L6-v2"

print(f"Checking path: {DATA_DIR}")

# 2. Check existence
if os.path.exists(DATA_DIR):
    print(f"Path exists: YES")
    print(f"Is Directory: {os.path.isdir(DATA_DIR)}")
    print(f"Contents: {os.listdir(DATA_DIR)}")
else:
    print(f"Path exists: NO")

# 3. Try Loading
try:
    print("Attempting to load SentenceTransformer...")
    model = SentenceTransformer(DATA_DIR)
    print("SUCCESS: Model loaded.")
except Exception as e:
    print(f"FAILURE: {e}")
