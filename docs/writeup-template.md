### Project name
Aura-Med: Edge-Native Multimodal Respiratory Triage

### Your team
- [Your Name/Handle] - Project Lead & ML Engineer - Architecture design, model integration, and pipeline optimization.

### Problem statement
Every year, lower respiratory infections claim the lives of nearly 700,000 children globally, with 90% of these deaths occurring in sub-Saharan Africa and South Asia. In these rural, low-resource settings, Community Health Workers (CHWs) serve as the frontline defense. However, they lack access to the diagnostic tools—like X-rays or pulmonologists—necessary to accurately distinguish between a benign cough and a life-threatening condition like pneumonia or severe asthma. The nearest clinic capable of making this distinction can be hours away, and triage delays directly cost lives. The unmet need is a reliable, offline diagnostic support tool that can operate entirely on basic smartphones. 

Aura-Med addresses this exact problem. By transforming a smartphone into an expert clinical decision support system, it acts as a "Digital Resident." It enables CHWs to record a 5-second ambient cough, which is instantly triaged based on WHO (IMCI/IMAI) guidelines. A 70% reduction in diagnostic delay could save countless lives by prioritizing rapid transport for critical patients while reassuring the parents of healthy ones.

### Overall solution:
Aura-Med bridges the gap between state-of-the-art bioacoustics and clinical reasoning through a multimodal fusion pipeline built on Google's HAI-DEF ecosystem. Our architecture combines two powerhouse models to achieve agentic triage entirely offline:

1. **Acoustic Perception (HeAR):** We utilize Health Acoustic Representations (HeAR) to extract deep acoustic biomarkers from brief patient audio recordings. Unlike simple thresholding, HeAR isolates subtle pathological indicators like crackles, wheezes, and in-drawing that are impossible to detect with math alone.
2. **Clinical Reasoning (MedGemma):** We utilize MedGemma 1.5 4B-IT (INT4 quantized) as the reasoning engine. We don't just use it as a chatbot; instead, we pass the HeAR embeddings (via an SVM classifier) alongside the patient's age and respiratory rate directly into MedGemma. MedGemma then performs transparent, Chain-of-Thought reasoning to map these fused inputs to a specific WHO triage protocol (GREEN, YELLOW, RED) and an actionable treatment plan.

By explicitly separating the "listening" (HeAR) from the "reasoning" (MedGemma), Aura-Med achieves high fidelity diagnostic accuracy without the prohibitive computational overhead of a single end-to-end massive multimodal model. To prove this synergy, we validated our acoustic pipeline (HeAR + SVM) against the rigorous ICBHI 2017 respiratory sound dataset, achieving 75% accuracy. Crucially, the system demonstrated 80% specificity in ruling out healthy patients and 70% sensitivity in detecting pathological sounds—using acoustic features alone. 

### Technical details 
Aura-Med is explicitly designed for the "Edge of AI" track. Building for rural CHWs means internet dependency is a failure state. Our entire technical architecture is constrained by the need to run locally on a mid-tier Android device:

- **Model Quantization:** MedGemma 1.5 4B-IT is quantized to INT4 (~2.5GB). The frozen HeAR encoder adds roughly ~0.3GB, bringing total memory footprint well under the 4GB limit of typical edge hardware.
- **Offline Inference:** The pipeline operates with zero network calls, ensuring 100% HIPAA/privacy compliance and zero cost-per-query. Average inference latency on our validation runs (simulated edge environment) was under 2 seconds per patient.
- **Safety Architecture:** We implemented strict guardrails to prevent clinical harm. A deterministic "Danger Sign Override" bypasses the AI entirely if WHO critical signs (e.g., central cyanosis) are checked, immediately returning a RED alert. Furthermore, an audio quality gate (RMS noise detection) prevents the model from hallucinating diagnoses on poor-quality recordings. 
- **Scale and Deployment:** Our proof-of-concept pipeline is ready for LiteRT/TFLite export, paving the way for a lightweight Android application that could be deployed to thousands of CHWs via programs like Nigeria's NPHCDA. 
