import os
import modal

# 1. Define the Modal App and Resources
app = modal.App("aura-med-training")
data_volume = modal.Volume.from_name("aura-med-data", create_if_missing=True)

# Define the container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "libsndfile1")
    .pip_install(
        "tensorflow-cpu",  # CPU-only TF — avoids all CUDA/XLA issues
        "huggingface_hub",
        "librosa",
        "numpy",
        "pandas",
        "scikit-learn",
        "torch",
        "kaggle"
    )
)

# 2. Main Training Class/Functions
@app.function(
    image=image,
    volumes={"/data": data_volume},
    secrets=[
        modal.Secret.from_name("kaggle-secret"),
        modal.Secret.from_name("hf-secret")
    ],
    cpu=4,       # Use multi-core CPU instead of GPU
    memory=8192, # 8GB RAM
    timeout=3600  # 1 hour
)
def train_model():
    import numpy as np
    import pandas as pd
    import librosa
    import torch
    import tensorflow as tf
    from huggingface_hub import snapshot_download
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    
    DATA_PATH = "/data/icbhi"
    
    # --- Step 1: Download Data if missing ---
    # --- Step 1: Download Data if missing ---
    # Check if we actually have the data, not just the folder
    expected_subdir = "audio_and_txt_files"
    found_data = False
    for root, dirs, files in os.walk(DATA_PATH):
        if expected_subdir in dirs:
            found_data = True
            print(f"✅ Found existing data at: {os.path.join(root, expected_subdir)}")
            break

    if not found_data:
        print(f"📂 Downloading ICBHI dataset from Kaggle to {DATA_PATH}...")
        
        # 0. Validate Credentials
        k_user = os.environ.get("KAGGLE_USERNAME", "")
        if "@" in k_user:
            print(f"❌ ERROR: KAGGLE_USERNAME '{k_user}' looks like an email address.")
            print("👉 Kaggle API requires your *username* (from kaggle.json), not your email.")
            print("👉 Please recreate the secret: modal secret create kaggle-secret KAGGLE_USERNAME=your_username KAGGLE_KEY=...")
            raise ValueError("Invalid KAGGLE_USERNAME (email detected)")
            
        # Clean up potential partial install
        if os.path.exists(DATA_PATH):
            import shutil
            shutil.rmtree(DATA_PATH)
        os.makedirs(DATA_PATH, exist_ok=True)
        
        # We use the Kaggle CLI directly
        import subprocess
        try:
            print(f"DEBUG: KAGGLE_USERNAME length: {len(k_user)}")
            result = subprocess.run(
                ["kaggle", "datasets", "download", "-d", "vbookshelf/respiratory-sound-database", "-p", DATA_PATH, "--unzip"],
                check=False, # Catching manually to print stderr
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Kaggle download failed (code {result.returncode})")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                if "403" in result.stderr or "401" in result.stderr:
                    print("👉 This usually means THE KEY IS INVALID or you need to accept terms at https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database/settings")
                raise RuntimeError(f"Kaggle download failed: {result.stderr}")
            
            print("✅ Kaggle download successful.")
            data_volume.commit()
        except Exception as e:
            print(f"❌ Error during Kaggle operation: {e}")
            raise e
        
        # Verify download
        print("📂 Directory structure after download:")
        for root, dirs, files in os.walk(DATA_PATH):
            level = root.replace(DATA_PATH, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files[:5]:
                print(f"{subindent}{f}")
            if len(files) > 5:
                print(f"{subindent}... ({len(files)-5} more files)")
    
    # --- Step 2: Load HeAR Model ---
    print("🔄 Loading HeAR model...")
    model_id = "google/hear"
    
    # Explicitly use token from secrets if available
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    model_dir = snapshot_download(model_id, token=hf_token)
    
    hear_model = tf.saved_model.load(model_dir)
    infer = hear_model.signatures["serving_default"]
    
    # --- Step 3: Parse Annotations and Extract Embeddings ---
    print("🔍 Parsing ICBHI annotations and extracting embeddings...")
    
    # Recursive search for audio_and_txt_files
    # The new dataset might have a different structure, we'll look for .wav files
    audio_dir = None
    for root, dirs, files in os.walk(DATA_PATH):
        # The ICBHI dataset usually has a folder with hundreds of .wav and .txt files
        wav_count = len([f for f in files if f.endswith(".wav")])
        if wav_count > 100:
            audio_dir = root
            print(f"✅ Found audio directory with {wav_count} files at: {audio_dir}")
            break
            
    if not audio_dir:
        # Fallback to any directory containing wav files if no large cluster found
        for root, dirs, files in os.walk(DATA_PATH):
            if any(f.endswith(".wav") for f in files):
                audio_dir = root
                break
                
    if not audio_dir:
        raise FileNotFoundError(f"Could not find any audio files in dataset at {DATA_PATH}")
        
    X = []
    y = []
    
    # Sample files to find labels
    annotation_files = [f for f in os.listdir(audio_dir) if f.endswith(".txt")]
    print(f"Found {len(annotation_files)} annotation files.")
    
    count = 0
    max_cycles = 7000 # Use full dataset for maximum accuracy
    
    for txt_file in annotation_files:
        if count >= max_cycles:
            break
            
        base_name = txt_file.rsplit('.', 1)[0]
        wav_path = os.path.join(audio_dir, base_name + ".wav")
        if not os.path.exists(wav_path):
            continue
            
        # Load audio (16kHz mono)
        audio, _ = librosa.load(wav_path, sr=16000, mono=True)
        
        # Read cycle annotations
        with open(os.path.join(audio_dir, txt_file), 'r') as f:
            for line in f:
                parts = line.strip().split() # start, end, crackle, wheeze
                if len(parts) < 4: continue
                
                try:
                    start, end = float(parts[0]), float(parts[1])
                    crackle, wheeze = int(parts[2]), int(parts[3])
                except ValueError: continue
                
                # Derive label: 0=Normal, 1=Crackle, 2=Wheeze, 3=Both
                if crackle == 1 and wheeze == 1: label = 3
                elif crackle == 1: label = 1
                elif wheeze == 1: label = 2
                else: label = 0
                
                # Extract audio slice
                start_idx = int(start * 16000)
                end_idx = int(end * 16000)
                cycle_audio = audio[start_idx:end_idx]
                
                if len(cycle_audio) == 0: continue
                
                # HeAR expects 2s (32000 samples)
                target_len = 32000
                if len(cycle_audio) > target_len:
                    cycle_audio = cycle_audio[:target_len]
                else:
                    cycle_audio = np.pad(cycle_audio, (0, target_len - len(cycle_audio)))
                
                # HeAR Inference
                input_tensor = np.expand_dims(cycle_audio, axis=0)
                output = infer(x=tf.constant(input_tensor, dtype=tf.float32))
                embedding = output['output_0'].numpy().squeeze() # (512,)
                
                X.append(embedding)
                y.append(label)
                count += 1
                
                if count % 100 == 0:
                    print(f"Extracted {count} cycle embeddings...")

    X = np.array(X)
    y = np.array(y)
    
    print(f"✅ Extraction complete. Dataset size: {X.shape}")
    
    # --- Step 4: Train Non-Linear SVM ---
    print("🚀 Training SVM classifier (RBF kernel)...")
    
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    import joblib
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
    
    # SVC with RBF kernel handles non-linear relationships
    clf = SVC(
        C=1.0, 
        kernel='rbf', 
        probability=True,      # Needed for confidence scores
        class_weight='balanced'
    )
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"📊 Accuracy: {acc:.1%}")
    print("Detailed Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Crackle", "Wheeze", "Both"]))
    
    # --- Step 5: Export Model ---
    print("💾 Exporting SVM model...")
    # Bundle scaler and clf together
    model_bundle = {
        "scaler": scaler,
        "svm": clf,
        "acc": acc,
        "labels": ["Normal", "Crackle", "Wheeze", "Both"]
    }
    
    weights_path = "/data/clinical_svm_model.joblib"
    joblib.dump(model_bundle, weights_path)
    data_volume.commit()
    
    print(f"✨ Success! SVM Model saved to Modal Volume: {weights_path}")
    
    return {
        "status": "success",
        "acc": float(acc),
        "model_path": weights_path
    }



@app.local_entrypoint()
def main():
    print("🏁 Starting Modal training job...")
    print("💡 Make sure you created 'kaggle-secret' in Modal with KAGGLE_USERNAME and KAGGLE_KEY.")
    
    # Run the remote function
    result = train_model.remote()
    
    print("\n✅ Training finished!")
    print(f"🏆 Final Accuracy: {result['acc']:.1%}")
    print("\nNext step: Run 'modal volume get aura-med-data linear_probe_weights.pt models/' to download the weights.")

if __name__ == "__main__":
    app.run()
