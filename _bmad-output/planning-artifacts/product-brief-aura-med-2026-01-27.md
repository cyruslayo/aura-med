---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments:
  - docs/project-description.md
  - docs/architecture-blueprint.md
  - docs/clinical-workflow.md
  - docs/data-engineering.md
  - docs/submission-checklist.md
date: 2026-01-27
author: Cyrus
---

# Product Brief: aura-med

## Executive Summary

**Aura-Med** is a multimodal, offline-first clinical decision support system that empowers Community Health Workers (CHWs) in Nigeria and other low-resource settings to diagnose respiratory diseases—particularly pneumonia and tuberculosis—with the accuracy of a trained clinician, using only a smartphone and a patient's cough recording.

By fusing Google's **HeAR** (Health Acoustic Representations) bioacoustic encoder with **MedGemma 2B** clinical reasoning, Aura-Med transforms a 5-second audio recording into a WHO IMCI-aligned triage recommendation in under 10 seconds—**no internet required, no cloud dependency**.

> **Why Now?** This exact stack was impossible to build 12 months ago. MedGemma's clinical reasoning and HeAR's acoustic biomarker extraction only became available in 2025. Aura-Med is the first solution to fuse these capabilities for edge deployment.

**The core promise:** A CHW can now diagnose like a trained clinician using only a $100 Android phone—enabling a **70% reduction in diagnostic delay** for pediatric respiratory diseases.

---

## Core Vision

### Problem Statement

Respiratory diseases like pneumonia and tuberculosis are the **leading killers of children under 5 in Nigeria**. Community Health Workers—the backbone of frontline healthcare in underserved regions—lack access to diagnostic tools, specialized training, or nearby facilities. Today, they diagnose by **guessing based on symptoms**, leading to dangerous delays in treatment, preventable suffering, and death.

### A Day Without Aura-Med

Aminat walks 3 kilometers to a rural village. A mother brings her a 2-year-old with a persistent cough. Aminat examines the child—no stethoscope, no labs, no X-ray. She thinks it's probably just a cold. She tells the mother to give fluids and rest.

Two weeks later, that child is in the regional hospital with advanced pneumonia. Aminat carries that guilt.

### A Day With Aura-Med

Same village, same child. Aminat opens the app, records 5 seconds of coughing, enters the respiratory rate. In 8 seconds, she sees:

> **🟡 YELLOW ALERT — PNEUMONIA**  
> Administer oral Amoxicillin. Follow up in 48 hours.

She acts immediately. That child's life is saved.

### Problem Impact

- **Late detection** leads to late treatment, preventable suffering, and death
- **Unnecessary referrals** overburden distant hospitals and waste scarce resources
- **CHW burnout** from high-stakes decisions without adequate support
- **Families bear the cost** of traveling to facilities that may not even help

### Why Existing Solutions Fall Short

| Gap | Reality |
|-----|---------|
| **No affordable tools** | CHWs have nothing beyond a stethoscope (if that) |
| **Training barriers** | Clinical interpretation requires years of training |
| **Infrastructure dependency** | Existing AI solutions require stable internet |
| **Technical complexity** | Current tools demand expertise CHWs don't have |
| **Cost** | Diagnostic equipment is prohibitively expensive for rural clinics |

### Proposed Solution

**Aura-Med** puts AI-powered respiratory diagnostics directly in CHWs' hands:

1. **Record** — CHW records patient's cough and breathing sounds via mobile app
2. **Analyze** — HeAR extracts acoustic biomarkers; MedGemma reasons over findings
3. **Triage** — App delivers WHO IMCI-aligned recommendation (Green/Yellow/Red)
4. **Act** — CHW follows clear next steps: home care, antibiotics, or urgent referral

All processing happens **on-device**—zero cloud dependency, runs on $100 Android phones with no SIM card.

### Key Differentiators

| Differentiator | Why It Matters |
|----------------|----------------|
| **Multimodal AI Fusion** | Fuses audio biomarkers with clinical reasoning—not just pattern matching |
| **True Offline Edge AI** | Zero cloud dependency—runs on $100 Android phones with no SIM card |
| **WHO IMCI-Aligned** | Outputs map directly to protocols CHWs already trust and use daily |
| **Google HAI-DEF Foundation** | Built on state-of-the-art health AI—not retrofitted consumer models |
| **Perfect Timing** | This exact stack was impossible before 2025—MedGemma + HeAR just became available |

---

## Target Users

### Primary User: The Community Health Worker

**Persona: Aminat Okonkwo**

| Attribute | Details |
|-----------|---------|
| **Role** | Community Health Worker (CHW) |
| **Education** | School of Health Technology graduate |
| **Environment** | Rural Nigeria—alternates between clinic-based work and village-to-village home visits |
| **Device** | Owns her own Android smartphone |
| **Motivation** | Genuine care for her community; driven by purpose, not just pay |

**Current Reality:**
Aminat sees 20-30 patients per day, many with respiratory complaints. Without diagnostic tools, she guesses based on symptoms—hoping she doesn't miss a pneumonia case that could kill a child. Every wrong call weighs on her conscience.

**Her Fears:**
- *"What if the AI is wrong and I trust it?"*
- *"What if it makes me look incompetent to my supervisors?"*
- *"What if patients don't trust technology over my judgment?"*

**What She Needs:**
A tool that fits her workflow, works without internet, and gives her confidence in her triage decisions. She doesn't need to understand the AI—she needs actionable guidance she can trust.

---

### Secondary Users

| User Type | Priority | Role | Interaction with Aura-Med |
|-----------|----------|------|---------------------------|
| **Trainers/Administrators** | 🔴 Critical | Onboard and support CHWs | Configure app settings, run training sessions, track adoption—**gatekeepers to successful rollout** |
| **Supervisors** | 🟡 V1.5 | Review CHW performance | Access triage reports to monitor quality (future analytics feature) |
| **District Health Officers** | 🟢 Roadmap | Manage regional health data | Aggregate diagnostic data for surveillance (future reporting feature) |

---

### Influencers & Decision Makers

| Tier | Stakeholder | Role in Adoption |
|------|-------------|------------------|
| **Tier 1: Funders** | International Donors (USAID, Gates Foundation, WHO programs) | Ultimate gatekeepers—evaluate efficacy, cost-per-diagnosis, alignment with national health strategy |
| **Tier 2: Channels** | NGOs funding CHW programs | Execution layer—deploy Aura-Med to CHW networks after donor approval |
| **Tier 3: Champions** | Ministry of Health officials, Clinic directors | Policy alignment, local advocacy, regulatory approval |

---

### User Journey: Aminat's Path to Impact

| Stage | Experience |
|-------|------------|
| **Discovery** | Learns about Aura-Med through her NGO employer during a quarterly training update |
| **Onboarding** | Quick 30-minute training session—app walkthrough, practice recording, sample triage |
| **First Use** | Records a coughing child's audio; receives her first AI-powered triage recommendation |
| **Trust Building** | First 5-10 cases: double-checks AI against her gut. Validates accuracy. Trust begins |
| **"Aha!" Moment** | First accurate pneumonia diagnosis she would have missed—realizes this changes everything |
| **Handling Uncertainty** | App shows "Inconclusive"—she knows to request re-recording or escalate to supervisor |
| **Daily Integration** | Uses Aura-Med for every patient with respiratory complaints; extension of her clinical judgment |
| **Advocacy** | Champions the tool to fellow CHWs; her confidence and accuracy improve measurably |

---

## Success Metrics

### 🌟 North Star Metric

> **Correct Triages per CHW per Week**
> 
> Combines adoption (they're using it), accuracy (triages are correct), and productivity (doing it at scale). This is THE metric funders will track.

---

### User Success: Aminat's Perspective

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Fewer Missed Cases** | >85% sensitivity for pneumonia/TB | Compare AI triage vs. gold-standard diagnosis |
| **Time Saved** | <10 seconds per triage | App telemetry: record → result timestamp |
| **Trust Building** | <5 cases to first independent use | Self-reported via app prompt |

**Inferred Satisfaction (No Surveys Required):**

| Signal | What It Tells You | Target |
|--------|-------------------|--------|
| Completion Rate | Does she finish the triage flow? | >95% |
| Return Rate | Does she use the app again tomorrow? | >80% daily active |
| Feature Adoption | Explores settings vs. basic use only | Progressive increase |

---

### Clinical Outcome Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Sensitivity** | >85% | AI output vs. chest X-ray/lab culture |
| **Specificity** | >70% | AI output vs. confirmed healthy cases |
| **Positive Predictive Value (PPV)** | >80% | Referrals → confirmed diagnoses at hospital |
| **Time-to-Treatment** | <24 hours | App timestamp → treatment administered |
| **Referral Accuracy** | >90% admission rate for 'Red Alert' | Track urgent referrals → hospital outcomes |

> **Future Validation:** Case Fatality Rate Reduction—compare mortality in Aura-Med villages vs. control groups.

---

### Business & Adoption Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Cost-per-Diagnosis** | <$0.50/triage | Competitive with paper screening; scales affordably |
| **CHW Adoption Rate** | >80% active after 30 days | Proves tool fits workflow |
| **Triage Throughput** | 2x patients screened/day | Productivity gain justifies investment |
| **Training Time** | <1 hour to competency | Low barrier to mass rollout |
| **Device Compatibility** | 90% of CHW-owned phones | No hardware procurement needed |

---

### Edge AI Performance (Kaggle Prize Criteria)

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Inference Latency** | <10 seconds | Real-time clinical workflow |
| **Memory Footprint** | <4GB peak RAM | Mid-range Android compatibility |
| **Battery Consumption** | <5% per 10 triages | All-day field usability |
| **Offline Capability** | 100% functionality | Essential for rural deployment |

---

### Leading Indicators (Early Warning Signals)

| Indicator | Red Flag Threshold | What It Tells You |
|-----------|--------------------|-------------------|
| **Re-recording Rate** | >30% | Audio quality issues |
| **Audio Quality Score** | <0.6 confidence | Hardware/environment problem (not model) |
| **Inconclusive Rate** | >20% | Model needs tuning |
| **Time-to-First-Triage** | >5 minutes | Onboarding friction |
| **Weekly Active Users** | <50% after week 2 | Workflow mismatch |

---

## MVP Scope

### Core Features (Must Have for Kaggle Submission)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Audio Recording** | CHW records 5-second cough/breathing sample via mobile app | 🔴 Critical |
| **Audio Preprocessing** | Resample to 16kHz mono, peak normalization, segment into 2s chunks | 🔴 Critical |
| **HeAR Embedding Extraction** | Process audio → 512-dim acoustic biomarker vector | 🔴 Critical |
| **Vitals Input Form** | Simple form: age (months), respiratory rate (bpm) | 🔴 Critical |
| **MedGemma Triage Reasoning** | Fuse audio embeddings + vitals → Chain-of-Thought clinical reasoning | 🔴 Critical |
| **WHO IMCI Recommendation** | Output Green/Yellow/Red triage with actionable next steps | 🔴 Critical |
| **Result Display Card** | Visual triage result with color-coded alert and action steps | 🔴 Critical |
| **Offline Inference** | 100% on-device processing, no internet required | 🔴 Critical |

**MVP User Flow:**
1. Open app → 2. Record cough (5s) → 3. Enter vitals (age, RR) → 4. View triage card → 5. Follow action steps

---

### Grey Zone (Explicitly Scoped Decisions)

| Feature | Decision | Rationale |
|---------|----------|-----------|
| **Retry flow for "Inconclusive"** | ✅ IN SCOPE | Critical UX—CHW must know what to do when uncertain |
| **Audio quality feedback** | ✅ IN SCOPE | "Recording too quiet/noisy" prompt before processing |
| **Basic error handling** | ✅ IN SCOPE | Graceful failure states, not crashes |
| **Settings screen** | ❌ OUT OF SCOPE | No configuration needed for demo |
| **Onboarding tutorial** | ❌ OUT OF SCOPE | Training is external to app |
| **Multi-patient sessions** | ❌ OUT OF SCOPE | One patient at a time for MVP |

---

### Out of Scope for MVP

| Feature | Rationale | Target Phase |
|---------|-----------|--------------|
| Supervisor dashboards | Not needed for Kaggle demo | V1.5 (Post-Pilot) |
| Multi-language support | English-only for competition | V1.5 |
| Historical patient data | No patient records for MVP | V2.0 |
| Cloud sync | Offline-first is the differentiator | V2.0 |
| Analytics/reporting | Focus on core triage first | V1.5 |
| Multi-disease support | Respiratory only for MVP | V2.0+ |

> **Scope Philosophy:** Say "no" to everything that doesn't directly win Kaggle or save a child's life.

---

### MVP Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Benchmark Accuracy** | >85% sensitivity, >70% specificity | Test against ICBHI/CODA TB holdout set |
| **Kaggle Submission Accepted** | Complete 3-page writeup + 3-min video + code | Submission confirmation |
| **Edge Performance** | <10s inference, <4GB RAM | Benchmarked on mid-range Android device |
| **Demo Quality** | Polished video showing CHW workflow | Judges can follow the user journey |

**Go/No-Go Decision:** If benchmark accuracy <80% sensitivity, revisit model fusion approach before submission.

---

### Fallback Architecture (Risk Mitigation)

| Risk | Fallback Strategy |
|------|-------------------|
| **MedGemma INT4 underperforms** | Test INT8 or FP16 quantization (larger but accurate) |
| **HeAR+MedGemma fusion fails** | Fall back to HeAR-only classifier (simpler, less reasoning) |
| **Inference exceeds 10s** | Reduce MedGemma context window or simplify prompt |
| **RAM exceeds 4GB** | Offload HeAR and MedGemma to sequential inference (slower but fits) |

> **Resilience Note:** Fallbacks show judges we've anticipated failure modes—not just the happy path.

---

### Future Vision

**Phase 1: Post-Kaggle Pilot (3-6 months)**
- Supervisor dashboards for quality monitoring
- Multi-language support (Hausa, Yoruba, Igbo)
- Field validation with real CHWs in 2-3 Nigerian states

**Phase 2: Scale (12-18 months)**
- Expand beyond Nigeria (Kenya, Tanzania, Uganda)
- Integration with national health information systems
- Additional disease modules (malaria, diarrhea)

**Phase 3: Platform (2-3 years)**
- Aura-Med becomes the CHW diagnostic platform for Sub-Saharan Africa
- Multi-modal inputs: cough + skin images + vitals
- White-label deployment for international health organizations
