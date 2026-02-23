import torch
import os
from src.models.clinical_classifier import ClinicalClassifier

def test_svm_integration():
    print("\n🔍 Testing SVM Integration...")
    
    # Path to our new model
    model_path = "models/clinical_svm_model.joblib"
    
    if not os.path.exists(model_path):
        print(f"❌ FAIL: Model not found at {model_path}")
        return
        
    clf = ClinicalClassifier(model_path=model_path)
    
    if not clf.model_loaded:
        print("❌ FAIL: ClinicalClassifier failed to load model bundle.")
        return
        
    # Create a mock HeAR embedding (512-dim)
    # We'll try some random noise
    mock_embedding = torch.randn(1, 512)
    
    label, desc, conf = clf.predict(mock_embedding)
    
    print(f"✅ Label: {label}")
    print(f"✅ Description: {desc}")
    print(f"✅ Confidence: {conf:.1%}")
    
    if label in clf.LABELS:
        print("✨ Prediction successful and valid!")
    else:
        print(f"❌ FAIL: Invalid label returned: {label}")

if __name__ == "__main__":
    test_svm_integration()
