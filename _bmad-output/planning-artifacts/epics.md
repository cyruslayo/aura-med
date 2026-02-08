---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
---

# aura-med - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for aura-med, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can accept audio recording of cough sounds (5-10 seconds)
FR2: System can validate audio quality and flag low-confidence recordings
FR3: System can extract acoustic embeddings using HeAR encoder
FR4: System can accept patient age as input
FR5: System can accept manually-entered respiratory rate
FR6: System can accept presence/absence of danger signs
FR21: System can fuse HeAR embeddings with MedGemma via projection layer
FR22: System can load models within Colab memory constraints (<15GB)
FR7: System can classify audio patterns into respiratory disease categories
FR8: System can generate clinical reasoning using Chain-of-Thought
FR9: System can apply WHO IMCI triage logic (Green/Yellow/Red)
FR10: System can provide actionable treatment recommendations
FR11: System can display triage classification with confidence score
FR12: System can display clinical reasoning trace (transparent AI)
FR13: System can display recommended actions per WHO protocol
FR14: System can indicate when result is inconclusive
FR23: System can display visual output formatting (triage alert box)
FR24: System can log inference time for latency metrics
FR15: System can detect low audio quality and request re-recording
FR16: System can handle model uncertainty without false confidence
FR17: System can override to RED ALERT when danger signs present
FR18: Notebook can run end-to-end with one "Run All" command
FR19: Notebook can load sample demo data (ICBHI coughs)
FR20: Notebook can display validation metrics (sensitivity, latency)

### NonFunctional Requirements

NFR1: Inference latency <10 seconds per sample | Logged in notebook output
NFR2: Total notebook runtime <5 minutes | Timed Run All execution
NFR3: Peak memory <15GB VRAM | Colab T4 GPU constraint
NFR4: Model loading <60 seconds | Startup time after pip install
NFR5: Notebook runs with zero errors on Colab T4 | Clean Run All execution
NFR6: All dependencies install automatically | No manual intervention
NFR7: Sample data loads from included source | No external downloads required
NFR8: Sensitivity >85% on validation set | Confusion matrix output
NFR9: Specificity >70% on validation set | Confusion matrix output
NFR10: Graceful degradation when confidence <0.6 | "Inconclusive" output triggered

### Additional Requirements

- **Starter Template**: Clean Architecture Notebook Structure (Setup, Architecture, Visualization classes) as defined in Architecture.
- **Infrastructure**: Deployment Target is Google Colab T4.
- **Architecture Pattern**: Hybrid Repo Strategy - Develop in `src/`, sync to `submission_demo.ipynb`.
- **Safety Mechanism**: Implement Rule-Based Override for Danger Signs (bypasses AI) acting as a hard-coded Logic Gate.
- **Resource Enforcement**: Implement `@audit_resources` decorator to enforce <4GB RAM simulation and raise `EdgeConstraintViolation` if usage exceeds limit.
- **Visualization**: Decouple logic (`TriageResult`) from presentation (`NotebookRenderer` with HTML/CSS).
- **Data Validation**: Use Pydantic models for `PatientVitals`.
- **Communication**: No external API calls; all processing local.
- **Latency**: Asynchronous inference pipeline needed to handle 2-model sequential execution within 10s.

### FR Coverage Map

### FR Coverage Map

FR1: Epic 1 - Input mechanism for audio recording
FR2: Epic 2 - Quality check for input audio
FR3: Epic 1 - Core acoustic embedding extraction
FR4: Epic 1 - Basic patient demographic input
FR5: Epic 1 - Clinical vitals input
FR6: Epic 2 - Critical safety input for danger signs
FR7: Epic 1 - Base classification capability
FR8: Epic 1 - Generation of clinical reasoning text
FR9: Epic 2 - Mapping logic to standard WHO protocols
FR10: Epic 2 - Deriving actionable treatments from status
FR11: Epic 3 - Visual presentation of classification
FR12: Epic 3 - Visual presentation of reasoning trace
FR13: Epic 3 - Visual presentation of recommended actions
FR14: Epic 2 - Handling of inconclusive states
FR15: Epic 2 - Workflow for low-quality re-recording
FR16: Epic 2 - Handling of low confidence scores
FR17: Epic 2 - Deterministic override logic
FR18: Epic 1 - Foundation of one-click notebook execution
FR19: Epic 1 - Integration of test data
FR20: Epic 3 - Final validation and metrics display
FR21: Epic 1 - Cross-modal projection layer implementation
FR22: Epic 1 - Memory-safe model loading architecture
FR23: Epic 3 - Rich HTML/CSS output formatting
FR24: Epic 3 - Inference latency logging and display

## Epic List

## Epic List

### Epic 1: Core Intelligence Pipeline
Establish the functioning diagnostic engine within the notebook, enabling the ingestion of audio and vitals to produce raw clinical reasoning using HeAR and MedGemma under strict resource constraints.
**FRs covered:** FR1, FR3, FR4, FR5, FR7, FR8, FR18, FR19, FR21, FR22

### Epic 2: Clinical Safety & Protocol Adherence
Implement the critical safety layer that adheres to WHO IMCI protocols, enforces deterministic overrides for danger signs, and manages audio quality/uncertainty to ensure trusted, safe outputs.
**FRs covered:** FR2, FR6, FR9, FR10, FR14, FR15, FR16, FR17

### Epic 3: Impact Demonstration & Telemetry
Create the interactive "Product Experience" layer that visualizes triage results in high-fidelity mobile cards, displays resource telemetry to prove feasibility, and validates overall system performance.
**FRs covered:** FR11, FR12, FR13, FR20, FR23, FR24

## Epic 1: Core Intelligence Pipeline

Establish the functioning diagnostic engine within the notebook, enabling the ingestion of audio and vitals to produce raw clinical reasoning using HeAR and MedGemma under strict resource constraints.

### Story 1.1: Project Skeleton & Model Loading

As a developer,
I want to set up the notebook structure and model loading classes,
So that the environment is ready for inference.

**Acceptance Criteria:**

**Given** A clean Google Colab T4 environment
**When** The "Setup" and "Model Loading" cells are executed
**Then** All dependencies (PyTorch, Transformers, Librosa) check install successfully
**And** The `HeAREncoder` and `MedGemmaReasoning` classes are imported/defined
**And** Mock models load into memory within 60 seconds without OOM errors (FR18, FR22)

### Story 1.2: HeAR Encoder Integration

As a data scientist,
I want to extract embeddings from audio using HeAR,
So that we have a rich acoustic representation for analysis.

**Acceptance Criteria:**

**Given** A path to a valid .wav file (cough recording)
**When** `HeAREncoder.encode(audio_path)` is called
**Then** The audio is loaded and resampled to 16kHz
**And** A tensor of shape (1, 1024) (or model specific dim) is returned
**And** Files longer than 10s are truncated/padded correctly (FR1, FR3)

### Story 1.3: MedGemma Reasoning Engine

As a clinician,
I want the system to reason about the case using MedGemma,
So that I get a preliminary diagnosis based on the audio and vitals.

**Acceptance Criteria:**

**Given** A HeAR embedding and a structured string of patient vitals
**When** `MedGemmaReasoning.generate(embedding, vitals)` is called
**Then** A Chain-of-Thought reasoning string is generated explaining the findings
**And** A final structured `TriageResult` (Status, Confidence) is returned
**And** The projection layer (mocked or real) accepts the embedding input without error (FR7, FR8, FR21)

### Story 1.4: Pipeline Orchestration

As a user,
I want to provide audio and vitals and get a comprehensive result,
So that the diagnostic workflow is seamless and easy to use.

**Acceptance Criteria:**

**Given** Valid audio file and patient vitals (Age, RR)
**When** `AuraMedAgent.predict()` is called
**Then** It orchestrates Audio -> HeAR -> MedGemma flow sequentially
**And** Returns a unified `TriageResult` object containing reasoning and status
**And** Logs total execution time (must be <10s simulated) (FR4, FR5)

## Epic 2: Clinical Safety & Protocol Adherence

Implement the critical safety layer that adheres to WHO IMCI protocols, enforces deterministic overrides for danger signs, and manages audio quality/uncertainty to ensure trusted, safe outputs.

### Story 2.1: Safety & Danger Sign Overrides

As a safety officer,
I want the system to immediately flag danger signs (e.g., lethargy, convulsions),
So that critical cases are never missed by the AI.

**Acceptance Criteria:**

**Given** A patient input with `danger_signs=True` (or specific list)
**When** `SafetyGuard.check()` is called OR `Agent.predict()` is run
**Then** The system returns a RED ALERT status IMMEDIATELY
**And** The LLM inference is bypassed (saving time/risk)
**And** The reasoning explicitly states "Emergency Danger Signs Detected" (FR6, FR17)

### Story 2.2: Audio Quality Gate

As a user,
I want to know if my recording is too noisy or invalid,
So I can re-record instead of getting a wrong diagnosis.

**Acceptance Criteria:**

**Given** An audio file with high noise or low signal
**When** `HeAREncoder` processes the file
**Then** It raises a `LowQualityError` or returns a low confidence metric
**And** The Agent catches this and returns an INCONCLUSIVE status
**And** The output advises "Please re-record in a quieter environment" (FR2, FR14, FR15, FR16)

### Story 2.3: WHO IMCI Protocol Logic

As a clinician,
I want the output to match exact WHO IMCI guidelines,
So I can trust the action plan is medically standard.

**Acceptance Criteria:**

**Given** A raw model classification (e.g., "Pneumonia", "Bronchiolitis")
**When** The result is formatted
**Then** It maps correctly to WHO Color Codes: Pneumonia -> YELLOW, Normal -> GREEN, Severe -> RED
**And** Displays the correct treatment text (e.g., "Oral Amoxicillin", "Soothe throat")
**And** No non-standard treatments are suggested (FR9, FR10)

## Epic 3: Impact Demonstration & Telemetry

Create the interactive "Product Experience" layer that visualizes triage results in high-fidelity mobile cards, displays resource telemetry to prove feasibility, and validates overall system performance.

### Story 3.1: Resource Telemetry & Constraints

As a judge,
I want to see that the system consumes <4GB RAM,
So I know it is feasible for edge deployment on low-cost devices.

**Acceptance Criteria:**

**Given** An inference task is running
**When** The `@audit_resources` decorator wraps the execution
**Then** It estimates/measure RAM and FLOPs usage
**And** It logs "Simulated RAM: X.X GB" to the console
**And** Raises `EdgeConstraintViolation` if usage exceeds 4GB (simulated or real) (FR24)

### Story 3.2: Notebook Renderer & Triage Cards

As a user,
I want to see a beautiful, mobile-style triage card,
So I understand the result quickly and feel the "product quality".

**Acceptance Criteria:**

**Given** A `TriageResult` object (Red, Yellow, or Green)
**When** `NotebookRenderer.render()` is called
**Then** It returns an HTML object with inline CSS
**And** The card acts as a visual "Mobile Screen" in the notebook output
**And** It uses the correct color theme and typography (Inter/Roboto) (FR11, FR13, FR23)

### Story 3.3: End-to-End Demo Journey

As a judge,
I want to run the full demo with one click,
So I can verify the solution works as promised.

**Acceptance Criteria:**

**Given** The notebook is open in Colab
**When** "Run All" is clicked
**Then** The "Journey 1" cell executes clearly
**And** It processes the sample audio and shows the Triage Card
**And** A latency table is displayed at the end showing <10s per sample performance
**And** Three scenarios are demonstrated: Success, Danger Override, and Inconclusive (FR18, FR20)
