# Kaggle Presentation Script — Aura-Med

**Target Audience:** Kaggle Competition Judges, Healthcare Innovators
**Duration:** ~3 minutes (Voice Over)
**Tone:** Informative, Impactful, Technical yet Accessible

---

## Slide 1: The Hook & The Problem
**Visual:** A powerful image of a crowded, low-resource clinic, perhaps transitioning into a sobering statistic about respiratory mortality worldwide.

**Voice Over:**
> "Every year, lower respiratory infections claim millions of lives globally. From pneumonia to severe asthma and COPD, misdiagnosis or delayed treatment is common in low-resource settings. In rural clinics around the world, health workers are the frontline defense, but they often lack the diagnostic tools—like X-rays or pulmonologists—needed to distinguish between a benign cough and a life-threatening condition. Mis-triage leads directly to avoidable mortality."

---

## Slide 2: The Solution – Aura-Med
**Visual:** An animated graphic of a smartphone listening to a cough, seamlessly transitioning to a clean, offline digital "Triage Card" interface.

**Voice Over:**
> "Aura-Med changes this paradigm. It transforms an ordinary, offline smartphone into an expert clinical decision support system. Designed for communities that lack stable internet or electricity, Aura-Med acts as a 'Digital Resident' that 'hears' and 'reasons.' It's a multimodal, agentic solution that democratizes access to high-quality respiratory diagnostics."

---

## Slide 3: Under the Hood (Technical Architecture)
**Visual:** High-level architectural flowchart. 
1. Audio input → HeAR (Encoder)
2. Projection Layer → MedGemma
3. Text Vitals + Audio → Final Output (Diagnosis & Triage)

**Voice Over:**
> "Here is how it works under the hood. When a clinician records a patient's cough or breathing sounds, the raw audio is processed by Google's HeAR—Health Acoustic Representations. HeAR translates the audio into deep acoustic biomarkers, capturing subtleties like crackles and wheezes. A custom projection layer bridges these audio features directly into the embedding space of MedGemma 1.5. Our system then processes both the acoustic signatures and the patient's vitals to produce a transparent, Chain-of-Thought reasoning, mapping directly to WHO triage protocols."

---

## Slide 4: Validation & The ICBHI Dataset
**Visual:** Confusion matrix showing 75% accuracy, with Sensitivity and Specificity metrics overlaid. Reference the ICBHI dataset explicitly.

**Voice Over:**
> "To prove Aura-Med's capability, we validated our acoustic pipeline against the rigorous, widely recognized ICBHI 2017 respiratory sound database — a gold-standard dataset with doctor-confirmed diagnoses across a broad population. Our HeAR encoder combined with a trained SVM classifier achieved 75% accuracy, with 80% specificity in ruling out healthy patients and 70% sensitivity in detecting pathological sounds like crackles and wheezes. Crucially, this validation was done using acoustic features alone — no vitals, no shortcuts. HeAR's embeddings genuinely capture the clinical biomarkers that distinguish a benign cough from pneumonia, COPD, or bronchiolitis."

---

## Slide 5: The Impact & Call to Action
**Visual:** Aura-Med logo, GitHub/Kaggle project links, overlaid on an image of a confident community health worker.

**Voice Over:**
> "Because Aura-Med runs entirely on the edge, it operates at zero cost per query with complete patient privacy. A model quantized for mobile hardware means no 5G, no cloud—just immediate answers. We believe every cough tells a clinical story. Aura-Med helps the world's most crucial healthcare workers listen, understand, and save lives."
