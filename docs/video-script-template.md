# Video Script Template — Aura-Med (3 minutes)

## 0:00–0:30 — The Hook (Emotional Impact)
> "Pneumonia kills 700,000 children every year. That's one child every 45 seconds.
> In rural Nigeria, the nearest clinic is hours away. Community Health Workers like Aminat
> are the first — and often only — line of defense. But they have no diagnostic tools."

**Visual:** Title card with the stat, then a map of Nigeria highlighting rural areas.

## 0:30–1:30 — Live Demo (Technical Proof)
> "Aura-Med changes this. Watch."

1. Open Colab notebook → Click "Run All"
2. Show model loading (HeAR + MedGemma)
3. Journey 1: Successful pneumonia detection → show triage card (YELLOW)
4. Journey 2: Emergency override → show RED card (danger signs bypass AI)
5. Journey 3: Low quality audio → INCONCLUSIVE (safety guard)

> "Three scenarios, all handled correctly. Notice the latency — under 5 seconds per case."

## 1:30–2:15 — Architecture (HAI-DEF Integration)
> "Here's how it works under the hood."

**Visual:** Architecture diagram showing:
- HeAR encoder processes cough audio → 512-dim embedding
- Projection Layer bridges audio → clinical feature space
- MedGemma 1.5 4B-IT (INT4 quantized) reasons over projected features + vitals
- WHO IMCI protocol mapping → actionable triage

> "The key innovation is the projection layer — it transforms raw acoustic biomarkers
> into clinically meaningful features that MedGemma can reason about."

## 2:15–2:45 — Validation (Quantitative Evidence)
> "We validated against the ICBHI 2017 respiratory sound database — a gold-standard dataset with doctor-confirmed diagnoses."

**Visual:** Show confusion matrix and metrics table from notebook (75% accuracy, 80% specificity, 70% sensitivity).

> "Using acoustic features alone — no vitals, no shortcuts — our HeAR plus SVM pipeline
> achieved 75% accuracy with 80% specificity and 70% sensitivity across 20 patients.
> This proves the system genuinely hears the difference between a healthy cough and pneumonia."

## 2:45–3:00 — Vision & Call to Action
> "Aura-Med runs entirely offline. No internet, no cloud, no cost per query.
> With further validation and clinical partnerships, this could reach
> the 1.5 billion people who lack access to basic diagnostics.
> Every cough tells a story. Aura-Med helps CHWs listen."

**Visual:** Aura-Med logo, GitHub link, Kaggle link.
