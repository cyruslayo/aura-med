import os
import requests

# Dictionary of sample files and their source URLs
SAMPLES = {
    "sample_A_cough_male.wav": "https://github.com/karolpiczak/ESC-50/raw/master/audio/1-52266-A-24.wav",
    "sample_B_cough_female.wav": "https://upload.wikimedia.org/wikipedia/commons/b/be/Woman_coughing_three_times.wav",
    "sample_C_cough_child.wav": "https://github.com/karolpiczak/ESC-50/raw/master/audio/5-233160-A-24.wav",
    "sample_D_heavy_breathing.wav": "https://github.com/karolpiczak/ESC-50/raw/master/audio/5-189721-A-26.wav" # Actually labeled as breathing in ESC-50
}

TARGET_DIR = "c:\\AI2025\\aura-med\\data\\samples"
os.makedirs(TARGET_DIR, exist_ok=True)

print(f"⬇️ Downloading samples to {TARGET_DIR}...")

for filename, url in SAMPLES.items():
    filepath = os.path.join(TARGET_DIR, filename)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

print("\n✨ Done! You can now use these files for testing.")
