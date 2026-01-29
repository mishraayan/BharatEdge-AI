import os
from sentence_transformers import SentenceTransformer

# Test 1: Absolute path with forward slashes (common fix for Windows/HF issues)
raw_path = os.path.join(os.getcwd(), "models", "embeddings", "all-MiniLM-L6-v2")
clean_path = raw_path.replace("\\", "/")

print(f"Testing Normalized Path: {clean_path}")

try:
    print("Attempt 1: Standard Load")
    model = SentenceTransformer(clean_path)
    print("SUCCESS: Loaded with forward slashes.")
except Exception as e:
    print(f"FAIL 1: {e}")

try:
    print("\nAttempt 2: local_files_only=True")
    model = SentenceTransformer(clean_path, device='cpu', local_files_only=True)
    print("SUCCESS: Loaded with local_files_only.")
except Exception as e:
    print(f"FAIL 2: {e}")
