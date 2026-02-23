---
stepsCompleted: [step-01-init, step-02-discovery, step-03-success, step-04-journeys, step-05-domain, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-aura-med-2026-01-27.md
  - docs/project-description.md
  - docs/architecture-blueprint.md
  - docs/clinical-workflow.md
  - docs/data-engineering.md
  - docs/submission-checklist.md
workflowType: 'prd'
documentCounts:
  briefs: 1
  research: 0
  projectDocs: 5
date: 2026-01-28
classification:
  projectType: notebook-demo
  domain: healthcare
  complexity: high
  projectContext: brownfield
  deploymentTarget: google-colab
  competitionFocus:
    impactVision: 40%
    videoStorytelling: 30%
    technicalFeasibility: secondary
    edgeAI: bonus-prize-only
---

# Product Requirements Document - aura-med

**Author:** Cyrus
**Date:** 2026-01-28
**Competition:** MedGemma Impact Challenge (Kaggle)

---

## Success Criteria

### Core Impact Statement

> **"Pneumonia: #1 infectious killer of children. 700,000 deaths/year. Faster diagnosis could save 1 in 4."**

### User Success (Aminat — Community Health Worker)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Triage Confidence | CHW trusts result within <5 cases | "I would have been wrong" moment |
| Time to Decision | <60 seconds from recording | vs. 48+ hours current practice |
| Usability | Zero training for basic use | Works on familiar Android device |

### Competition Success (Kaggle Judges)

| Criterion | Weight | Target |
|-----------|--------|--------|
| Impact & Vision | 40% | "Every 45 seconds, a child dies from pneumonia" |
| Video Storytelling | 30% | Aminat's uncertainty → AI clarity → child saved |
| HAI-DEF Usage | — | HeAR + MedGemma multimodal fusion |
| Technical Feasibility | — | >85% sensitivity, <10s inference |

### Technical Success (Colab Demo)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sensitivity | >85% | vs. ICBHI/CODA TB test set |
| Specificity | >70% | Reduce false positives |
| Inference Latency | <10 seconds | On Colab T4 GPU |
| One-Click Run | 100% reproducible | No manual dependency fixes |

---

## Product Scope

### MVP — Kaggle Submission

- ✅ Audio recording → HeAR embedding extraction
- ✅ MedGemma triage reasoning (Chain-of-Thought)
- ✅ WHO IMCI-aligned output (Green/Yellow/Red)
- ✅ 3-minute video pitch
- ✅ 3-page technical writeup
- ✅ Clean, reproducible Colab notebook

### Growth Features (Post-Competition)

- Multi-language support (Hausa, Yoruba, Igbo)
- Supervisor dashboards
- Historical patient tracking

### Vision (Future)

- Edge deployment on $100 Android phones
- Expansion to Kenya, Tanzania, Uganda
- Multi-disease modules (malaria, diarrhea)

---

## User Journeys

### Journey 1: Aminat's Triage (Success Path)

**Persona:** Aminat Okonkwo — CHW, rural Nigeria, Android phone, no internet

**Opening Scene:**
Aminat arrives at a village home. A mother holds her 2-year-old who has been coughing for three days. Aminat examines the child—no stethoscope, no labs. She thinks it's probably just a cold but feels uncertain.

**Rising Action:**
She opens Aura-Med, holds her phone near the child, and records 5 seconds of coughing. She enters the child's age (14 months) and respiratory rate (48 bpm). She taps "Analyze."

**Climax:**
8 seconds later, the screen shows:
> **🟡 YELLOW ALERT — PNEUMONIA**
> "Administer oral Amoxicillin. Follow up in 48 hours."

Aminat's face changes. *She would have sent this child home.*

**Resolution:**
She gives the first dose of amoxicillin from her kit. She schedules a follow-up. That child will live because Aminat had the right tool at the right moment.

---

### Journey 2: Aminat's Triage (Edge Case — Inconclusive)

**Scene:**
Same village, different child. Recording is noisy (crying, market sounds). Aminat taps "Analyze."

**Result:**
> **⚪ INCONCLUSIVE**
> "Audio quality low (confidence: 0.4). Please re-record in a quieter environment."

**Recovery:**
Aminat takes the mother to a quieter room. Re-records. This time:
> **🟢 GREEN — COUGH OR COLD**
> "Soothe throat, fluids, rest. No antibiotics needed."

**Insight:** The system fails gracefully—no false confidence, clear guidance for recovery.

---

### Journey 3: Kaggle Judge's Notebook Review

**Persona:** Dr. Sarah — Google Research scientist, evaluating 50+ submissions

**Opening Scene:**
Dr. Sarah opens your Colab notebook. She has 10 minutes per submission.

**Rising Action:**

| Cell | What She Sees | Her Reaction |
|------|---------------|--------------|
| 1 | Title + Problem Statement | "Okay, pneumonia in Nigeria. Clear." |
| 2 | Impact stat: "700K deaths/year" | "That's significant." |
| 3 | Data pipeline runs | "No errors. Good." |
| 4 | HeAR + MedGemma architecture | "Interesting multimodal approach." |
| 5 | Demo: Triage a sample cough | "Let me see the output..." |
| 6 | WHO IMCI result with reasoning | "This is well thought out." |
| 7 | Metrics table | "85% sensitivity. Solid." |

**Climax:**
She watches your 3-minute video. Aminat's story. The child saved. She feels something.

**Resolution:**
She scores your submission high on Impact (40%) and Storytelling (30%). Your notebook is in the top 10.

---

### Journey Requirements Summary

| Journey | Capabilities Required |
|---------|----------------------|
| Aminat Success | Audio recording, HeAR embedding, MedGemma reasoning, IMCI output |
| Aminat Edge Case | Audio quality detection, retry flow, graceful degradation |
| Judge Review | Clean notebook structure, one-click run, compelling narrative |

---

## Domain-Specific Requirements (Healthcare)

### Model Safety (Implemented in Demo)

| Requirement | Implementation |
|-------------|----------------|
| Graceful Degradation | If `Acoustic_Confidence < 0.6`, output "Inconclusive" |
| Uncertainty Handling | Clear guidance: "Re-record in quieter environment" |
| WHO Protocol Alignment | Outputs mapped to IMCI Green/Yellow/Red |

### Deployment Path (Post-Competition)

> **Regulatory Considerations:** Production deployment would require FDA Software as Medical Device (SaMD) 510(k) clearance, HIPAA-compliant data handling, and IRB-approved clinical validation. The architecture supports this through modular pipelines, Chain-of-Thought traces, and audit-ready output formatting.

### Technical Constraints (Demo Scope)

| Constraint | Target |
|------------|--------|
| Data Privacy | Demo uses only public datasets (ICBHI, CODA TB) |
| Clinical Accuracy | >85% sensitivity benchmark required |
| Inference Transparency | MedGemma provides reasoning trace |

---

## Innovation & Novel Patterns

### What's New

> **Aura-Med is the first solution to fuse HeAR acoustic biomarker extraction with MedGemma clinical reasoning for edge deployment.**

Existing solutions either use acoustic analysis (without medical reasoning) or LLMs (without audio understanding). Aura-Med combines both—giving CHWs the diagnostic confidence of a specialist, powered by a smartphone.

**The result:** A CHW in rural Nigeria can make specialist-grade triage decisions in under 60 seconds, without internet.

### Technical Innovation

| Component | Source | Role |
|-----------|--------|------|
| HeAR | Google (2024) | Acoustic understanding |
| MedGemma 1.5 4B-IT | Google (2025) | Clinical reasoning |
| Projection Layer | Our contribution | Learned audio-to-text alignment |

The projection layer uses learned audio-to-text alignment, trained on supervised cough-to-diagnosis pairs, to bridge the semantic gap between acoustic embeddings and clinical language.

> *This architecture was impossible to build 12 months ago.*

---

## Notebook Demo Specific Requirements

### Input Data Sources

| Input | Source | Method |
|-------|--------|--------|
| Audio Recording | Phone microphone | 5-10 second cough recording |
| Respiratory Rate | CHW observation | Manual breath count (60s) |
| Child Age | Caregiver interview | Entered by CHW |
| Danger Signs | Physical examination | CHW visual/manual check |

### Notebook Structure

| Cell | Type | Content |
|------|------|--------|
| 0 | Code | GPU check, VRAM status |
| 1 | Markdown | Title + Problem + Impact (700K deaths/year) |
| 2 | Code | Dependencies (pip install) |
| 3 | Code | Model loading (HeAR + MedGemma) |
| 4 | Code | Sample data loading (ICBHI) |
| 5 | Code | HeAR embedding extraction |
| 6 | Code | MedGemma clinical reasoning |
| 7 | Code | Full demo: Triage flow |
| 8 | Code | Metrics table (sensitivity, latency) |
| 9 | Markdown | Conclusion + Reproducibility checklist |

### Technical Requirements

| Requirement | Target |
|-------------|--------|
| Runtime | Google Colab (T4 GPU) |
| One-Click | Must run all cells without errors |
| Memory | <15GB peak VRAM |
| Inference | <10 seconds per sample |
| Demo Data | 3-5 sample coughs from ICBHI |

### Demo Output Format

```
╔═════════════════════════════════════════════════════════╗
║  🟡 YELLOW ALERT — PNEUMONIA SUSPECTED                   ║
╠═════════════════════════════════════════════════════════╣
║  Confidence: 87%                                         ║
║  Action: Administer oral Amoxicillin. Follow up 48hrs.   ║
╚═════════════════════════════════════════════════════════╝

📋 Clinical Reasoning (WHO IMCI):
• Respiratory Rate: 48 bpm (elevated for 14mo)
• Acoustic Pattern: Crackles detected (0.82)
• Risk Level: Moderate (YELLOW zone)
```

### Reproducibility Checklist

- ✅ Runs on Colab T4 GPU without modifications
- ✅ All dependencies install automatically
- ✅ Sample data included in notebook
- ✅ Total runtime: <5 minutes
- ✅ Peak memory: <12GB VRAM

---

## Project Scoping & Timeline

### Competition Deadline

> **February 24, 2026** (27 days from PRD creation)

### Sprint Plan

| Week | Dates | Focus | Deliverable |
|------|-------|-------|-------------|
| 1 | Jan 28 - Feb 3 | Core Pipeline | HeAR + MedGemma working in Colab |
| 2 | Feb 4 - Feb 10 | Evaluation | Metrics on ICBHI, demo flow complete |
| 3 | Feb 11 - Feb 17 | Polish | Notebook narrative, reproducibility |
| 4 | Feb 18 - Feb 24 | Deliverables | Video pitch, writeup, final test |

### Key Milestones

| Milestone | Target Date |
|-----------|-------------|
| HeAR embedding extraction | Feb 3 |
| MedGemma reasoning pipeline | Feb 7 |
| End-to-end demo working | Feb 10 |
| Metrics validation (>85% sensitivity) | Feb 14 |
| Polished notebook (one-click) | Feb 17 |
| Video pitch recorded | Feb 21 |
| Technical writeup complete | Feb 22 |
| Final submission | Feb 24 |

### Scope Cuts (Post-Competition)

| Feature | Reason |
|---------|--------|
| Android app prototype | No time |
| Multi-language support | Scope creep |
| Edge quantization | Nice-to-have for Edge AI prize |

### Critical Path

```
HeAR works → MedGemma works → Fusion works → Metrics pass → Polish → Submit
```

> **Risk:** Any blocker in Weeks 1-2 puts submission at risk.

---

## Functional Requirements

### Audio Processing

- FR1: System can accept audio recording of cough sounds (5-10 seconds)
- FR2: System can validate audio quality and flag low-confidence recordings
- FR3: System can extract acoustic embeddings using HeAR encoder

### Clinical Input

- FR4: System can accept patient age as input
- FR5: System can accept manually-entered respiratory rate
- FR6: System can accept presence/absence of danger signs

### Model Integration

- FR21: System can fuse HeAR embeddings with MedGemma via projection layer
- FR22: System can load models within Colab memory constraints (<15GB)

### Clinical Reasoning

- FR7: System can classify audio patterns into respiratory disease categories
- FR8: System can generate clinical reasoning using Chain-of-Thought
- FR9: System can apply WHO IMCI triage logic (Green/Yellow/Red)
- FR10: System can provide actionable treatment recommendations

### Output & Display

- FR11: System can display triage classification with confidence score
- FR12: System can display clinical reasoning trace (transparent AI)
- FR13: System can display recommended actions per WHO protocol
- FR14: System can indicate when result is inconclusive
- FR23: System can display visual output formatting (triage alert box)
- FR24: System can log inference time for latency metrics

### Graceful Degradation

- FR15: System can detect low audio quality and request re-recording
- FR16: System can handle model uncertainty without false confidence
- FR17: System can override to RED ALERT when danger signs present

### Demo & Reproducibility

- FR18: Notebook can run end-to-end with one "Run All" command
- FR19: Notebook can load sample demo data (ICBHI coughs)
- FR20: Notebook can display validation metrics (sensitivity, latency)

---

## Non-Functional Requirements

### Performance

| NFR | Requirement | Measurement |
|-----|-------------|-------------|
| NFR1 | Inference latency <10 seconds per sample | Logged in notebook output |
| NFR2 | Total notebook runtime <5 minutes | Timed Run All execution |
| NFR3 | Peak memory <15GB VRAM | Colab T4 GPU constraint |
| NFR4 | Model loading <60 seconds | Startup time after pip install |

### Reliability & Reproducibility

| NFR | Requirement | Measurement |
|-----|-------------|-------------|
| NFR5 | Notebook runs with zero errors on Colab T4 | Clean Run All execution |
| NFR6 | All dependencies install automatically | No manual intervention |
| NFR7 | Sample data loads from included source | No external downloads required |

### Clinical Accuracy

| NFR | Requirement | Measurement |
|-----|-------------|-------------|
| NFR8 | Sensitivity >85% on validation set | Confusion matrix output |
| NFR9 | Specificity >70% on validation set | Confusion matrix output |
| NFR10 | Graceful degradation when confidence <0.6 | "Inconclusive" output triggered |
