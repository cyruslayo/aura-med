# Aura-Med: Edge-Native Universal Respiratory Triage

![Aura-Med Concept](https://img.shields.io/badge/Status-Kaggle_Submission-blue) ![License](https://img.shields.io/badge/License-MIT-green)

Aura-Med is an offline, edge-capable clinical decision support system designed for Community Health Workers (CHWs) in low-resource settings. It transforms a standard smartphone into a "Digital Resident" capable of triaging respiratory diseases (like Pneumonia, COPD, and URTI) for patients of **any age** — from neonates to the elderly — using only a brief ambient cough recording and basic patient vitals.

Created for the **MedGemma Impact Challenge (Edge AI Special Prize)**.

## 🌟 Key Features

*   **Universal Age Support:** Dynamically applies **6 distinct age-group thresholds** with dual WHO protocols — **IMCI** (Integrated Management of Childhood Illness) for pediatrics and **IMAI** (Integrated Management of Adolescent and Adult Illness) for adults.
*   **Multimodal Fusion:** Combines **Google's HeAR** (Health Acoustic Representations) bioacoustic embeddings with an **SVM classifier** and **MedGemma 1.5 4B-IT** clinical reasoning.
*   **100% Offline Capability:** Designed to run entirely on edge hardware (quantized to ~2.8GB footprint) with zero internet dependency, ensuring HIPAA compliance and $0 cost-per-query.
*   **Safety First:** Deterministic "Danger Sign" overrides bypass the AI to instantly flag critical patients. An audio quality gate (RMS thresholding) rejects silent or clipped recordings. Robust parsing strips internal thinking tokens and uses negative lookbehinds to prevent false positives.
*   **Validated Performance:** The acoustic pipeline (HeAR + SVM) achieved **75% Accuracy, 80% Specificity, and 70% Sensitivity** on a balanced 20-patient subset validated against the [ICBHI 2017 Respiratory Sound Database](https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database).

## 🏗️ Technical Architecture

Aura-Med intentionally separates "Perception" from "Reasoning" to maintain a low memory footprint suitable for mobile devices.

1.  **Acoustic Perception (HeAR):** An audio clip is captured and processed by the frozen `HeAR` encoder, extracting a 512-dimensional acoustic biomarker embedding.
2.  **Clinical Classification (SVM):** A trained Support Vector Machine (SVM) classifies the HeAR embeddings into clinical labels — Normal, Crackle, Wheeze, or Both — with confidence scores.
3.  **Age-Adaptive Prompt Synthesis:** The acoustic findings are fused with structured patient vitals (Age, Respiratory Rate, Danger Signs) into an age-adaptive prompt that encodes the correct WHO thresholds for the patient's demographic.
4.  **Agentic Reasoning (MedGemma):** The fused prompt is passed to `MedGemma 1.5 4B-IT (INT4)`, which generates transparent, Chain-of-Thought reasoning and a final triage classification (🟢 GREEN, 🟡 YELLOW, 🔴 RED) with an actionable, age-appropriate treatment plan.

## 📊 Dataset

This project uses the **ICBHI 2017 Respiratory Sound Database** for training and validation of the acoustic classifier.

*   **Kaggle Link:** [Respiratory Sound Database](https://www.kaggle.com/datasets/vbookshelf/respiratory-sound-database)
*   Contains 920 annotated respiratory sound recordings from 126 patients across 6 clinical settings.
*   Diagnoses include: Healthy, COPD, Pneumonia, URTI, Bronchiectasis, Bronchiolitis, and LRTI.

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

The primary way to interact with Aura-Med is through the interactive Jupyter Notebook.

### Universal Triage Pipeline (Kaggle Submission Demo)
Run the [`aura_med_universal_triage.ipynb`](notebooks/aura_med_universal_triage.ipynb) notebook. This notebook demonstrates:
*   End-to-end inference using the HeAR → SVM → MedGemma pipeline.
*   Age-adaptive triage logic across 6 demographic groups (neonates through elderly).
*   ICBHI dataset validation with confusion matrix and classification report.
*   Interactive audio upload and triage generation.

### Core API Example

```python
from src.agent.core import AuraMedAgent
from src.datatypes import PatientVitals

# Initialize the pipeline (loads HeAR, SVM, and MedGemma)
agent = AuraMedAgent()

# Define patient vitals
vitals = PatientVitals(
    age_months=24,
    respiratory_rate=45,  # Fast breathing for a 2-year-old
    danger_signs=False,
    unable_to_drink=False,
    vomits_everything=False,
    convulsions=False,
    lethargic=False,
)

# Run inference on an audio file
result = agent.predict("path/to/cough.wav", vitals)

print(f"Status: {result.status}")
print(f"Action: {result.action_recommendation}")
print(f"Reasoning: {result.reasoning}")
```

## 📂 Project Structure

```text
aura-med/
├── data/                  # Sample audio files and testing data
├── docs/                  # Write-ups, presentation scripts, and architecture specs
├── notebooks/
│   └── aura_med_universal_triage.ipynb  # Main pipeline & validation notebook
├── src/
│   ├── agent/             # Core AuraMedAgent, protocols, and triage logic
│   ├── models/            # HeAR encoder, MedGemma reasoning, and SVM classifier wrappers
│   ├── utils/             # Audio processing, logging, and metrics helpers
│   ├── datatypes.py       # PatientVitals and TriageResult data models
│   └── config.py          # Centralized environment and path configuration
├── tests/                 # Unit and integration test suite (pytest)
└── requirements.txt       # Python dependencies
```

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (Note: MedGemma is subject to its own Google terms of use).
