---
stepsCompleted:
  - 1
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/product-brief-aura-med-2026-01-27.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-01-29.md
  - docs/architecture-blueprint.md
  - docs/clinical-workflow.md
  - docs/data-engineering.md
  - docs/project-description.md
  - docs/submission-checklist.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-01-29'
project_name: 'aura-med'
user_name: 'Cyrus'
date: '2026-01-29'
---

# Architecture Decision Document


## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The system is a specialized diagnostic tool focusing on a single critical workflow: pediatric respiratory triage. Startlingly simple user surface (Record -> Analyze -> Act) belies deep technical complexity.
*   **Input:** Multi-modal (Audio + Structured Vitals).
*   **Processing:** Novel orchestration of frozen encoders (HeAR) and quantized reasoning models (MedGemma).
*   **Output:** Structured clinical text (WHO IMCI protocols) + Visual Triage Cards (simulated in Notebook).
*   **Safety:** Explicit "Inconclusive" logic and "Danger Sign" overrides are first-class functional citizens.

**Non-Functional Requirements:**
*   **Edge-Native constraints define the architecture**: The <4GB RAM and <10s inference targets dictate model selection (2B params) and quantization strategies (INT4) immediately.
*   **Offline Requirement**: Precludes any API-based LLMs or cloud offloading.
*   **Reproducibility**: The Colab T4 constraint serves as the "deployment environment" for the MVP.
*   **User Trust (Reliability):** System must be deterministic and handle uncertainty gracefully to maintain trust.

**Scale & Complexity:**
*   Primary domain: **Edge AI / Clinical Decision Support**
*   Complexity level: **High** (Algorithmic & Constraint complexity) / **Low** (Feature surface area)
*   Estimated architectural components: **5 Core Components** (Audio Processor, HeAR Encoder, Projection Bridge, MedGemma LLM, Notebook Visualization Renderer)

### Technical Constraints & Dependencies

*   **Environment:** **Google Colab T4 (Strict MVP Target)**. The "App" is a simulation within the notebook.
*   **Hardware Proxy:** Must prove feasibility for Arm64 Android (<4GB RAM) via explicit logging/metrics, but implementation remains in Python/Notebook.
*   **Models:** Must use **Google HeAR** and **Gemma** family models.
*   **Quantization:** INT4 quantization is mandatory for memory fit.
*   **Latency:** Asynchronous inference pipeline needed to handle 2-model sequential execution within 10s.

### Cross-Cutting Concerns Identified

1.  **Clinical Safety & Hallucination Control:** Deterministic guardrails (Prompt Engineering + Output Parsing) are architectural.
2.  **Resource Management:** Explicit VRAM management (loading/unloading or shared context) is required.
3.  **Visualization Separation:** Decouple `TriageResult` (logic) from `NotebookRenderer` (HTML/CSS presentation) to ensure code quality while delivering a "wow" demo.

## Starter Template Evaluation

### Primary Technology Domain
**Kaggle Notebook Demo** (Python/Jupyter environment acting as a system simulation).

### Starter Options Considered
*   **Monolithic Notebook:** Single stream of execution. Rejected due to poor readability and "spaghetti code" risk.
*   **Hidden Utility Scripts:** Abstraction via external files. Rejected because it hides the innovative "Projection Layer" logic from judges who need to see the code to score "Technical Feasibility".
*   **Clean Architecture Notebook:** Modular cells using Python classes for logical separation (Setup, Architecture, Visualization). Selected for balance of readability and demonstrable engineering rigor.

### Selected Starter: Clean Architecture Notebook Structure

**Rationale for Selection:**
Aligns with the "Demo as UX" strategy. The notebook structure itself tells the architectural story to the primary user (The Judge).

**Project Structure (Notebook Cells):**
1.  **System Setup:** `pip install`, Model Checks (GPU/RAM validation).
2.  **Architecture Layer:** `class HeAREncoder`, `class MedGemmaReasoning`, `class AuraMedAgent`.
3.  **Visualization Layer:** `display_triage_card(result)` (HTML/CSS rendering).
4.  **The Demo Story:** "Journey 1: Aminat's Success" (Executable cells).

**Architectural Decisions Provided by Starter:**
*   **Language:** Python 3.10+ (Colab default).
*   **Frameworks:** PyTorch (HeAR), Transformers (MedGemma), IPython.display (Visualization).
*   **Visualization:** HTML/CSS injected directly into notebook output for "Mobile Card" simulation.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
*   **Real Inference Pipeline (Hybrid/Real):** We will execute the actual frozen HeAR encoder and quantized MedGemma model within the notebook. We accept the risk of OOM errors (managed via resource checks) in exchange for proving technical feasibility.
*   **Deterministic Safety Overrides:** "Danger Sign" inputs (e.g., lethargy) will trigger a hard-coded Logic Gate that bypasses the LLM entirely, ensuring 100% safety for critical cases regardless of AI performance.
*   **Explicit Edge Telemetry (Enforced):** We will implement an `@audit_resources` decorator to calculate and log theoretical FLOPs and RAM usage for every inference call. **Critically, this will raise an `EdgeConstraintViolation` exception if usage exceeds 4GB**, proving feasibility via strict enforcement.

### Data Architecture
*   **Storage:** Ephemeral/In-Memory (Python Dictionaries) for the duration of the notebook session.
*   **Validation:** Pydantic models (or strict TypeHints) for validating input `PatientVitals` before they touch the model.

### Authentication & Security (Safety Focus)
*   **Safety as Security:** The **Rule-Based Override** is the primary security feature.
*   **Privacy:** All processing is local to the runtime; no external API calls (e.g., to OpenAI) are permitted.

### API & Communication Patterns
*   **Internal API:** The `AuraMedAgent` class encapsulates complexity. Methods: `.predict(audio, vitals)`.
*   **Error Handling:** "Inconclusive" is a valid return state, not an exception.

### Frontend Architecture (Notebook Visualization)
*   **Renderer Pattern:** Decoupled `NotebookRenderer` handles HTML/CSS presentation, keeping `AuraMedAgent` pure.
*   **Visuals:** `IPython.display.HTML` with inline f-string CSS for custom Triage Cards.
*   **Resource Visualization:** Triage Cards will include a 'Resource Bar' (e.g., `RAM: [||||..] 3.1GB`) to visually demonstrate Edge efficiency alongside clinical results.

### Infrastructure & Deployment
*   **Target:** Google Colab T4 Instance.
*   **Edge Simulation:** The "Deployment" is a successful run of the notebook that outputs the "Simulated Edge Usage" logs.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points:**
*   **Cell Discipline:** Preventing "Spaghetti Notebooks" (imports everywhere, global state leaks).
*   **Safety Signaling:** How to communicate "Danger" vs "Error" vs "Inconclusive".
*   **Data Structure:** Preventing "Dict Soup" by using strict dataclasses for internal flow.

### Naming Patterns
*   **Constants (Config):** `UPPER_SNAKE_CASE` at top of notebook (e.g., `MAX_RAM_GB = 4.0`).
*   **Components:** `PascalCase` classes (e.g., `HeAREncoder`, `AuraMedAgent`).
*   **Helpers:** `snake_case` functions (e.g., `load_audio_sample()`).
*   **Safety Variables:** Prefix with `safety_` (e.g., `safety_danger_signs_present`).

### Structure Patterns (The "Clean Notebook")
1.  **Phase 1: Setup:** Imports, Pip Installs, Global Config, Hardware Check.
2.  **Phase 2: Core Components:** The `HeAREncoder` and `MedGemmaReasoning` classes.
3.  **Phase 3: The Agent:** `AuraMedAgent` (The Orchestrator).
4.  **Phase 4: Optimization:** The `@audit_resources` decorator implementation.
5.  **Phase 5: Visualization:** `display_triage_card` and `NotebookRenderer`.
6.  **Phase 6: Demo Execution:** The runnable stories.

### Communication Patterns (Data Flow)
*   **Input:** `PatientVitals` (Dataclass) - *Never pass raw dicts to the model.*
*   **Output:** `TriageResult` (Dataclass) - *Contains `status` (Enum), `confidence` (float), `reasoning` (str), `usage_stats` (dict).*

### Process Patterns (Safety & Errors)
*   **Critical Safety:** `DangerSignException` -> Caught by Agent -> Returns strict **RED ALERT** result (Rule-Based).
*   **Resource Violation:** `EdgeConstraintViolation` -> **Uncaught Exception** (Stops execution to prove the test failed).
*   **Model Uncertainty:** `LowConfidenceError` -> Caught by Agent -> Returns **INCONCLUSIVE** result.

### Enforcement Guidelines
*   **No Global State Mutation:** Cells should not modify global variables defined in other cells (except for explicit Config at the top).

## Project Structure & Boundaries

### Complete Project Directory Structure
**Hybrid Repo Strategy:** We develop using standard Python tooling in `src/` for quality (testing, linting) and manually synchronize finalized classes into the `submission_demo.ipynb` cells.

```
aura-med/
├── README.md
├── requirements.txt         # For local dev environment
├── notebooks/
│   ├── submission_demo.ipynb # THE PRIMARY ARTIFACT (Jupyter)
│   └── experiments/          # Sandbox for HeAR exploration
├── src/                      # Local Dev Source (Mirrors Notebook Cells)
│   ├── config.py             # -> Cell 1 (Config & Setup)
│   ├── models/
│   │   ├── hear_encoder.py   # -> Cell 2 (HeAR Encoder Class)
│   │   ├── medgemma.py       # -> Cell 2 (MedGemma Reasoning Class)
│   ├── agent/
│   │   ├── core.py           # -> Cell 3 (AuraMedAgent Orchestrator)
│   │   └── safety.py         # -> Cell 3 (Safety Logic & Exceptions)
│   ├── visualization/
│   │   └── renderer.py       # -> Cell 5 (Notebook Renderer & Triage Cards)
│   └── utils/
│       └── resource_audit.py # -> Cell 4 (@audit_resources Decorator)
├── tests/                    # Local Unit Tests (Critical for logic verification)
│   └── test_agent.py
└── data/                     # Local sample wavs for testing
```

### Architectural Boundaries

**The Notebook Boundary:**
*   The `submission_demo.ipynb` is the **Self-Contained Deployment**.
*   It must NOT import from `src` during execution on Kaggle.
*   All `src` code must be copy-pasted into the respective Notebook Cells for the final submission.

**Component Boundaries:**
*   **Safety Layer:** `src/agent/safety.py` is the gatekeeper. It must not depend on the LLM. It operates on raw `PatientVitals`.
*   **Visualization Layer:** `src/visualization/renderer.py` owns all HTML/CSS. The Agent returns data (`TriageResult`); the Renderer makes it pretty.
*   **Model Layer:** `src/models/` encapsulates the heavy lifting (HeAR, Gemma). The Agent orchestrates them but doesn't know their internal tenure implementation.

### Requirements to Structure Mapping

**Epic 1 (Foundation):**
*   Mapped to: `src/models/` (Model loading), `src/agent/core.py` (Orchestration).
*   Notebook Location: Cell 2 (Models) & Cell 3 (Agent).

**Epic 2 (Safety):**
*   Mapped to: `src/agent/safety.py` (Rules & Exceptions).
*   Notebook Location: Cell 3 (Agent Logic).

**Epic 3 (UX/Demo):**
*   Mapped to: `src/visualization/renderer.py` (Triage Cards).
*   Notebook Location: Cell 5 (Visualization).

### Integration Points

**Data Flow:**
1.  **Input:** Audio File + `PatientVitals` -> `AuraMedAgent.predict()`
2.  **Safety Check:** `SafetyGuard.check(vitals)` (Throws `DangerSignException` if critical)
3.  **Inference:** `HeAREncoder.encode()` -> `MedGemmaReasoning.generate()`
4.  **Resource Audit:** `@audit_resources` wraps the inference step.
5.  **Output:** `TriageResult` object.
6.  **Display:** `IPython.display.HTML(render_card(result))`

### Development Workflow
1.  **Code:** Write/Edit class in `src/`.
2.  **Test:** Run `pytest tests/`.
3.  **Sync:** Copy class code to `submission_demo.ipynb`.

## Architecture Validation Results

### Coherence Validation ✅
*   **Strategy:** "Simulation as Truth" is consistent. The *Real* models run (Risk), but the *Edge* constraints are enforced via code (Safety), and the *UI* is purely illustrative (HTML).
*   **Structure:** The "Hybrid Repo" strategy perfectly balances the need for quality code in `src/` with the requirement for a single-file `submission_demo.ipynb` artifact.

### Requirements Coverage Validation ✅
*   **Foundation:** Covered by `src/models` and `src/agent`.
*   **Safety:** Covered by `DangerSignException` and the Rule-Based Override decision.
*   **UX/Impact:** Covered by `NotebookRenderer` and Triage Cards.
*   **Explicit Exclusions:** "User Auth" and "Database Persistence" are architecturally excluded as they are irrelevant for the single-session demo scope.

### Implementation Readiness Validation ✅
*   **Patterns:** Concrete patterns defined for naming (`safety_` prefix), structure (Cell mapping), and process (Manual Sync).
*   **Gap Analysis:** Identified minor gaps:
    1.  Need to define exact HeAR model version (Hugging Face ID).
    2.  Need a validation dataset of audio files for offline demo.

### Architecture Readiness Assessment
**Overall Status:** READY FOR IMPLEMENTATION
**Confidence Level:** High
**Key Strengths:**
*   **Honesty:** The explicit `@audit_resources` enforcement proves we aren't faking the edge capabilities.
*   **Safety:** The Rule-Based Override ensures the demo never "kills a patient" due to AI hallucination.
*   **Storytelling:** The `NotebookRenderer` ensures the visual output matches the impact narrative.

### Implementation Handoff
**First Implementation Priority:**
Initialize the **Hybrid Repo** structure (`src/`, `notebooks/`, `tests/`) and prove the manual sync workflow with a "Hello World" cell.
