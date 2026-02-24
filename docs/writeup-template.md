### Project name
Aura-Med: Edge-Native Universal Respiratory Triage

### Your team
- [Your Name/Handle] - Project Lead & ML Engineer - Architecture design, model integration, and pipeline optimization.

### Problem statement
Every year, lower respiratory infections claim millions of lives globally. While the burden heavily impacts children in sub-Saharan Africa and South Asia, respiratory diseases like COPD and pneumonia also severely affect adults and the elderly. In rural, low-resource settings, Community Health Workers (CHWs) serve as the frontline defense across all demographics. However, they lack access to the diagnostic tools—like X-rays or pulmonologists—necessary to accurately distinguish between a benign cough and a life-threatening condition. The nearest clinic capable of making this distinction can be hours away, and triage delays directly cost lives. The unmet need is a reliable, offline diagnostic support tool that provides universal age coverage and operates entirely on basic smartphones. 

Aura-Med addresses this exact problem. By transforming a smartphone into an expert clinical decision support system, it acts as a "Digital Resident" for patients of any age. It enables CHWs to record a brief ambient cough, which is instantly triaged based on an age-adaptive application of WHO (IMCI for pediatrics, IMAI for adults) guidelines. A massive reduction in diagnostic delay could save countless lives by prioritizing rapid transport for critical patients while reassuring those with benign conditions.

### Overall solution:
Aura-Med bridges the gap between state-of-the-art bioacoustics and clinical reasoning through a multimodal fusion pipeline built on Google's health AI models. Our architecture combines powerhouse models and dynamic logic to achieve agentic, universal triage entirely offline:

1. **Acoustic Perception (HeAR):** We utilize Health Acoustic Representations (HeAR) to extract deep acoustic biomarkers from brief patient audio recordings. Unlike simple thresholding, HeAR isolates subtle pathological indicators like crackles and wheezes.
2. **Clinical Classifier (SVM):** We map the 512-dimensional HeAR embeddings to clinical labels (Normal, Crackle, Wheeze, Both) and confidence scores using an SVM classifier trained on the rigorous ICBHI 2017 Respiratory Sound Database.
3. **Age-Adaptive Reasoning (MedGemma):** We utilize MedGemma 1.5 4B-IT (INT4 quantized) as the reasoning engine. We pass the acoustic classifications alongside the patient's age, respiratory rate, and danger signs into an age-adaptive prompt. MedGemma then performs transparent, Chain-of-Thought reasoning to correctly apply 6 distinct age-group thresholds and dual WHO protocols (IMCI/IMAI), dynamically mapping these fused inputs to a specific triage status (GREEN, YELLOW, RED) and an actionable, age-appropriate treatment plan.

By explicitly separating the "listening" from the "reasoning", Aura-Med achieves high fidelity diagnostic accuracy without the prohibitive computational overhead of a single massive multimodal model. To prove this synergy, our acoustic pipeline (HeAR + SVM) was validated against the ICBHI 2017 dataset on a balanced 20-patient subset (10 pathological, 10 healthy), achieving 75% accuracy, 80% specificity in ruling out healthy patients, and 70% sensitivity in detecting pathological sounds—using acoustic features alone. 

### Technical details 
Building for rural CHWs means internet dependency is a failure state. Our entire technical architecture is constrained by the need to run locally on a mid-tier Android device:

- **Model Quantization:** MedGemma 1.5 4B-IT is quantized to INT4 (~2.5GB). The frozen HeAR encoder adds roughly ~0.3GB, bringing total memory footprint well under the 4GB limit of typical edge hardware.
- **Offline Inference:** The pipeline operates with zero network calls, ensuring 100% HIPAA/privacy compliance and zero cost-per-query. Average end-to-end inference latency on our validation runs (simulated edge environment on a Colab T4 GPU) was typically under 15 seconds per patient.
- **Robust Parsing & Safety:** We implemented strict guardrails to prevent clinical harm. A deterministic "Danger Sign Override" bypasses the AI completely if critical signs are checked. An audio quality gate (RMS thresholding) rejects silent or clipped recordings before they can reach the model. Furthermore, our parsing logic strips MedGemma's internal thinking tokens and uses negative lookbehinds to prevent false positives (e.g., misinterpreting "no danger signs" as a RED alert).
- **Scale and Deployment:** Our proof-of-concept pipeline is designed with LiteRT/TFLite deployment in mind, paving the way for a lightweight Android application that could provide universal triage to thousands of CHWs via programs like Nigeria's NPHCDA. 
