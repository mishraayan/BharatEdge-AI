import os
import requests
from tqdm import tqdm

# Configuration
# Using Qwen2.5-3B-Instruct for better multilingual (Hindi/Indic) support
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
TARGET_FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")

def download_file(url, filename):
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    
    filepath = os.path.join(MODELS_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"[INFO] Model already exists at: {filepath}")
        return

    print(f"[INFO] Downloading model from {url}...")
    print(f"[INFO] Target: {filepath}")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    
    with open(filepath, 'wb') as f:
        for data in response.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    
    if total_size != 0 and t.n != total_size:
        print("[ERROR] Download failed or incomplete.")
    else:
        print("[SUCCESS] Model downloaded successfully.")

if __name__ == "__main__":
    download_file(MODEL_URL, TARGET_FILENAME)
