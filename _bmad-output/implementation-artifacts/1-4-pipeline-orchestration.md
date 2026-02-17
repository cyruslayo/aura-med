# Story 1.4: Pipeline Orchestration

Status: done

## Story

As a user,
I want to provide audio and vitals and get a comprehensive result,
so that the diagnostic workflow is seamless and easy to use.

## Acceptance Criteria

1. **Given** Valid audio file path and patient vitals (Age, RR)
   **When** `AuraMedAgent.predict(audio_path, vitals)` is called
   **Then** It orchestrates Audio -> HeAR -> MedGemma flow sequentially without manual intervention.

2. **Given** The inference pipeline is running
   **When** The `predict` method completes
   **Then** It returns a unified `TriageResult` object containing both the clinical reasoning string and the classification status (`RED`, `YELLOW`, `GREEN`, or `INCONCLUSIVE`).

3. **Given** A prediction request
   **When** The system executes
   **Then** It measures and logs the total execution time (latency), which must be <10s (simulated or real).

4. **Given** A missing or invalid dependency (e.g., model not loaded)
   **When** `predict()` is called
   **Then** It raises a clear error context (or handles gracefully via Inconclusive if appropriate, but setup errors should fail fast).

## Tasks / Subtasks

- [x] **Task 1: Define Agent Structure** (AC: #1)
  - [x] Create/Update `src/agent/core.py`
  - [x] Define `AuraMedAgent` class
  - [x] Implement `__init__` to initialize `HeAREncoder` and `MedGemmaReasoning` instances (composition).

- [x] **Task 2: Implement Orchestration Logic** (AC: #1, #2)
  - [x] Implement `predict(audio_path, vitals) -> TriageResult`
  - [x] Call `HeAREncoder.encode(audio_path)` to get embeddings
  - [x] Call `MedGemmaReasoning.generate(embeddings, vitals)` to get result
  - [x] Ensure data flow respects types (`PatientVitals` -> `TriageResult`).

- [x] **Task 3: Implement Latency Tracking** (AC: #3)
  - [x] Wrap the prediction logic with timing code (start/end timestamp)
  - [x] Log execution duration to console/logs
  - [x] Include duration in a `usage_stats` dictionary in the result (if `TriageResult` supports it, or valid side-channel).

- [x] **Task 4: Write Unit Tests** (AC: #1-4)
  - [x] Create `tests/test_agent.py`
  - [x] Mock `HeAREncoder` and `MedGemmaReasoning` to avoid loading heavy models
  - [x] Verify `predict` calls dependencies in correct order
  - [x] Verify latency logging meets `<10s` check in logic (if applicable)
  - [x] Test error propagation.

- [ ] **Task 5: Sync to Notebook** (AC: #1)
  - [ ] Copy `AuraMedAgent` code to the corresponding Cell (Cell 3: "The Agent")
  - [ ] Verify imports work in the notebook context
  - **Note:** Blocked due to .ipynb edit restrictions. Manual sync required by user.

## Dev Notes

### Technical Requirements
- **Orchestration**: The `AuraMedAgent` determines the flow. It must instantiate the sub-components.
- **Dependency Injection**: Consider passing model instances into `__init__` for easier testing, or instantiate them internally if "composition" is the strict pattern. Architecture suggests `AuraMedAgent` encapsulates complexity.
- **Latency**: Use `time.perf_counter()` for high-resolution timing.

### Architecture Patterns
- **Encapsulation**: `AuraMedAgent` is the public API. Users don't touch `HeArEncoder` directly.
- **Data Flow**: Audio Path (str) + Vitals (Dataclass) -> [Agent] -> Result (Dataclass).
- **Inconclusive Handling**: If `HeAREncoder` returns low confidence (future story), Agent must handle it. For now, assume happy path or basic error propagation.

### Project Structure Notes
- **File**: `src/agent/core.py`
- **Class**: `AuraMedAgent`
- **Tests**: `tests/test_agent.py`

### References
- [Architecture: API & Communication Patterns](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L105)
- [Architecture: Implement Patterns](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L140)
- [Story 1.3: MedGemma Interface](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/1-3-medgemma-reasoning-engine.md)
- [Story 1.2: HeAR Interface](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/1-2-hear-encoder-integration.md) (Implicit reference)

## Dev Agent Record

### Agent Model Used
Gemini 2.5 Pro

### Debug Log References
- Tests require PyTorch; user runs tests in Google Colab.

### Completion Notes List
- Created `AuraMedAgent` class in `src/agent/core.py` with dependency injection support.
- Implemented `predict()` method orchestrating HeAR -> MedGemma pipeline.
- Added latency tracking via `time.perf_counter()`, stored in `TriageResult.usage_stats`.
- Created comprehensive unit tests in `tests/test_agent.py` using mocks.
- Task 5 (notebook sync) blocked due to `.ipynb` edit restrictions - requires manual copy by user.

### Change Log
- 2026-02-02: Initial implementation of AuraMedAgent orchestrator.
- 2026-02-10: [AI-Review] Applied fixes for 4 High, 3 Medium issues:
  - Added SafetyGuard for danger sign override.
  - Added input validation for audio path and vitals.
  - Improved error wrapping and logging.
  - Fixed test bugs and added latency thresholds.

### File List
- src/agent/core.py (NEW)
- src/agent/__init__.py (MODIFIED)
- tests/test_agent.py (NEW)
