import os
import joblib
import numpy as np
import torch
from typing import Tuple

class ClinicalClassifier:
    """
    Converts HeAR 512-dimensional embeddings into clinical respiratory labels.
    
    Uses a trained SVM (RBF kernel) to identify adventitious 
    breath sounds such as crackles and wheezes.
    """
    
    LABELS = ["Normal", "Crackle", "Wheeze", "Both"]
    DESCRIPTIONS = {
        "Normal": "Normal breath sounds, no adventitious sounds detected.",
        "Crackle": "Crackles detected — discontinuous, explosive sounds suggesting fluid or inflammation in airways.",
        "Wheeze": "Wheezes detected — continuous, high-pitched sounds suggesting airway narrowing.",
        "Both": "Both crackles and wheezes detected — suggesting significant respiratory pathology (e.g., severe pneumonia/bronchiolitis)."
    }
    
    def __init__(self, model_path: str = "models/clinical_svm_model.joblib"):
        self.scaler = None
        self.svm = None
        self.model_loaded = False
        
        if os.path.exists(model_path):
            try:
                bundle = joblib.load(model_path)
                self.scaler = bundle["scaler"]
                self.svm = bundle["svm"]
                self.model_loaded = True
                print(f"✅ ClinicalClassifier: Loaded trained SVM model from {model_path}")
            except Exception as e:
                print(f"⚠️ ClinicalClassifier: Failed to load model ({e}). Clinical analysis will be disabled.")
        else:
            print(f"⚠️ ClinicalClassifier: Model not found at {model_path}. Please run training script first.")

    def predict(self, embedding: torch.Tensor) -> Tuple[str, str, float]:
        """
        Classify a HeAR embedding using the trained SVM.
        """
        if not self.model_loaded:
            return "Unknown", "Clinical model not loaded.", 0.0

        # Convert torch tensor to numpy for Scikit-learn
        if isinstance(embedding, torch.Tensor):
            x = embedding.detach().cpu().numpy()
        else:
            x = embedding
            
        # Standardize input
        if x.ndim == 1:
            x = x.reshape(1, -1)
        
        x_scaled = self.scaler.transform(x)
        
        # Get prediction and probabilities
        idx = self.svm.predict(x_scaled)[0]
        probs = self.svm.predict_proba(x_scaled)[0]
        
        label = self.LABELS[idx]
        description = self.DESCRIPTIONS[label]
        confidence = probs[idx]
        
        return label, description, float(confidence)
