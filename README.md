# Aura-Med: Edge-Native Multimodal Respiratory Triage

![Aura-Med Concept](https://img.shields.io/badge/Status-Kaggle_Submission-blue) ![License](https://img.shields.io/badge/License-MIT-green)

Aura-Med is an offline, edge-capable clinical decision support system designed for Community Health Workers (CHWs) in low-resource settings. It transforms a standard smartphone into a "Digital Resident" capable of diagnosing respiratory diseases (like Pneumonia, COPD, and Severe Asthma) using only a 5-second ambient cough recording and basic patient vitals. 

Created for the **MedGemma Impact Challenge (Edge AI Special Prize)**.

## 🌟 Key Features

*   **Multimodal Fusion:** Combines **Google's HeAR** (Health Acoustic Representations) bioacoustic embeddings with **MedGemma 1.5 4B-IT** clinical reasoning.
*   **100% Offline Capability:** Designed to run entirely on edge hardware (quantized to ~2.8GB footprint) with zero internet dependency, ensuring HIPAA compliance and $0 cost-per-query.
*   **WHO Protocol Alignment:** Triage logic strictly follows World Health Organization (WHO) IMCI and IMAI guidelines.
*   **Safety First:** Deterministic "Danger Sign" overrides bypass the AI to instantly flag critical patients, while ambient noise gating prevents hallucinations on poor-quality audio.
*   **Validated Performance:** The acoustic pipeline (HeAR + SVM) achieved **75% Accuracy, 80% Specificity, and 70% Sensitivity** when validated against the rigorous ICBHI 2017 Respiratory Sound Database.

## 🏗️ Technical Architecture

Aura-Med intentionally separates "Perception" from "Reasoning" to maintain a low memory footprint suitable for mobile devices.

1.  **Acoustic Perception:** A 5-second audio clip is captured and processed by the frozen `HeAR` encoder, extracting a 512-dimensional acoustic biomarker embedding.
2.  **Clinical Classification:** A trained Support Vector Machine (SVM) classifies the HeAR embeddings to detect adventitious lung sounds (Crackles, Wheezes).
3.  **Prompt Synthesis:** The acoustic findings are fused with structured patient vitals (Age, Respiratory Rate, SpO2, Danger Signs).
4.  **Agentic Reasoning:** The fused prompt is passed to `MedGemma 1.5 4B-IT (INT4)`, which generates a transparent, Chain-of-Thought reasoning block and final triage classification (🟢 GREEN, 🟡 YELLOW, 🔴 RED).

## 🚀 Getting Started

### Prerequisites

*   Python 3.10+
*   GPU recommended for rapid inference (NVIDIA T4 or better). The system falls back to a mocked "Demo Mode" if no GPU is detected.
*   A Hugging Face account and access token (to download MedGemma).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/cyruslayo/aura-med.git
    cd aura-med
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set your Hugging Face Token:**
    You must accept the Gemma 1.5 license agreement on Hugging Face before downloading the model.
    ```bash
    export HF_TOKEN="your_huggingface_token_here"
    ```

## 💻 Usage

The primary way to interact with Aura-Med is through our interactive Jupyter Notebooks.

### 1. Universal Triage Pipeline (Kaggle Submission Demo)
Run the `aura_med_universal_triage.ipynb` notebook. This notebook demonstrates:
*   End-to-end inference using the HeAR → MedGemma pipeline.
*   Age-adaptive triage logic (handling both Pediatric and Adult cases).
*   Interactive audio upload and triage generation.

### 2. Dataset Validation Pipeline
The `submission_demo.ipynb` notebook contains the full ICBHI 2017 validation suite, demonstrating how the acoustic pipeline was evaluated.

### Core API Example

```python
from src.agent.core import AuraMedAgent
from src.agent.types import PatientVitals

# Initialize the pipeline (loads HeAR, SVM, and MedGemma)
agent = AuraMedAgent()

# Define patient vitals
vitals = PatientVitals(
    age_months=24, 
    respiratory_rate=45, # Fast breathing for a 2-year-old
    temperature_c=38.5,
    danger_signs=[]
)

# Run inference on an audio file
result = agent.predict("path/to/cough.wav", vitals)

print(f"Status: {result.status}")
print(f"Action: {result.action}")
print(f"Reasoning: {result.reasoning}")
```

## 📂 Project Structure

```text
aura-med/
├── data/                  # Sample audio files and testing data
├── docs/                  # Write-ups, presentation scripts, and architecture specs
├── notebooks/             # Interactive Jupyter notebooks demonstrating the pipeline
├── src/
│   ├── agent/             # Core AuraMedAgent and data types
│   ├── models/            # HeAR encoder, MedGemma reasoning, and SVM classifier wrappers
│   ├── ui/                # Gradio UI components (if applicable)
│   ├── utils/             # Audio processing, logging, and metrics helpers
│   └── config.py          # Centralized environment and path configuration
├── tests/                 # Unit and integration test suite (pytest)
└── requirements.txt       # Python dependencies
```

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (Note: MedGemma is subject to its own Google terms of use).
