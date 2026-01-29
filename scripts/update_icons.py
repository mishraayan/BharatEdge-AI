from PIL import Image
import os

SOURCE = r"C:\Users\ayanm\.gemini\antigravity\brain\30da04da-bd9a-4417-8f12-41818960035d\bharatedge_app_icon_1769680462853.png"
DEST_DIR = r"c:\Users\ayanm\BharatEdge-AI\app\src-tauri\icons"

if not os.path.exists(SOURCE):
    print(f"Error: Source image not found at {SOURCE}")
    exit(1)

img = Image.open(SOURCE)

# 1. Save as ICO (Standard Windows Icon)
# ICO should include multiple sizes
img.save(os.path.join(DEST_DIR, "icon.ico"), format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print(f"Generated {DEST_DIR}\\icon.ico")

# 2. Save PNGs
sizes = {
    "32x32.png": (32, 32),
    "128x128.png": (128, 128),
    "128x128@2x.png": (256, 256),
    "icon.png": (512, 512) # Tauri uses this for some Linux/generic things
}

for name, size in sizes.items():
    resized = img.resize(size, Image.Resampling.LANCZOS)
    resized.save(os.path.join(DEST_DIR, name))
    print(f"Generated {DEST_DIR}\\{name}")
