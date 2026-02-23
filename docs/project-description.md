# Project Description: Aura-Med (The Respiratory Sentinel)

## 1. Overview

**Aura-Med** is a multimodal, agentic clinical decision support system designed to democratize access to high-quality respiratory diagnostics in low-resource settings. Built using **Google’s Health AI Developer Foundations (HAI-DEF)**, the application empowers Community Health Workers (CHWs) to accurately screen, triage, and manage life-threatening conditions like **Pneumonia** and **Tuberculosis (TB)** using only a low-cost, offline mobile device.

## 2. Problem Statement

In many regions, particularly across sub-Saharan Africa, the ratio of physicians to patients is critically low. Community Health Workers are the backbone of the healthcare system but often lack the specialized training or diagnostic tools (like X-rays or lab tests) to distinguish between a common cold and a fatal Lower Respiratory Infection (LRI).

**The Challenge:**

* **Mis-triage:** High rates of diagnostic delay leading to avoidable mortality.
* **Infrastructure:** Lack of stable internet (5G/Fiber) and electricity in rural clinics.
* **Cognitive Load:** High patient volumes leading to burnout and errors in protocol adherence.

## 3. Solution Concept: "The Multimodal Agent"

Aura-Med functions as a **"Digital Resident"** that "hears" and "reasons." It combines bioacoustic analysis with advanced LLM reasoning to provide a human-centered triage experience.

### Key Features:

* **Multimodal Bioacoustics:** Uses the **HeAR (Health Acoustic Representations)** model to analyze cough sounds for clinical biomarkers (crackles, wheezes).
* **Agentic Reasoning:** Uses **MedGemma 1.5 4B-IT** to ingest acoustic signatures and patient vitals to generate a **Chain-of-Thought (CoT)** reasoning trace.
* **Edge-Native:** Entirely offline inference using quantized models (INT4/GGUF) optimized for mobile hardware via **LiteRT**.
* **Protocol-Aligned:** Outputs are strictly mapped to the **WHO Integrated Management of Childhood Illness (IMCI)** guidelines.

## 4. Technical Architecture

The system utilizes a "Bridge" architecture to connect disparate foundation models:

1. **The Encoder (HeAR):** Converts raw audio waveforms into 512-dimensional embeddings.
2. **The Bridge (Projection Layer):** A trained MLP that maps audio embeddings into the MedGemma token embedding space.
3. **The Brain (MedGemma):** A 2-billion parameter model that performs the final triage based on the combined text-audio input.

## 5. Implementation Roadmap

* **Phase 1: Data Ingestion** – Processing the ICBHI and CODA TB datasets for multimodal training.
* **Phase 2: Model Fusion** – Developing the Projection Layer to bridge HeAR and MedGemma.
* **Phase 3: Optimization** – Quantizing the stack for on-device deployment.
* **Phase 4: Validation** – Benchmarking against WHO-standardized clinical cases.

## 6. Success Metrics & Impact

* **Sensitivity/Specificity:** Achieving >85% accuracy in distinguishing Pneumonia from viral coughs.
* **Latency:** <10 seconds for a full triage report on a mid-range Android device.
* **Human Impact:** Targeted reduction in diagnostic delay for pediatric pneumonia by up to 70% in pilot community settings.

---

