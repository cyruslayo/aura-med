# Story 3.3: End-to-End Demo Journey

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Judge,
I want to run the full demo with one click,
so that I can verify the solution works as promised.

## Acceptance Criteria

1. **Given** The notebook is open in Colab
2. **When** "Run All" is clicked
3. **Then** The "Journey 1" cell executes clearly
4. **And** It processes the sample audio and shows the Triage Card
5. **And** A latency table (markdown or HTML) is displayed at the end showing <10s per sample performance
6. **And** Three scenarios are demonstrated: Success, Danger Override, and Inconclusive (FR18, FR20)
7. **And** Total notebook execution time (excluding model downloads) is < 5 minutes (NFR2)
8. **And** Resource telemetry is visible for each scenario, showing < 4GB simulated RAM (NFR3)

## Tasks / Subtasks

- [x] **Task 1: Orchestrate Demo Scenarios** (AC: #3, #4, #6)
  - [x] Implement `Journey 1: Clinical Success` using a valid cough sample (e.g., `data/sample_normal.wav`).
  - [x] Implement `Journey 2: Emergency Override` using patient data with `lethargy=True`.
  - [x] Implement `Journey 3: Inconclusive Registry` using a noisy audio sample.
- [x] **Task 2: Performance Telemetry & Reporting** (AC: #5, #7, #8)
  - [x] Implement a `LatencyTracker` helper to collect timing from each scenario.
  - [x] Generate a summary table at the end of the notebook.
  - [x] Ensure `@audit_resources` output is captured/printed for each run.
- [x] **Task 3: Notebook Assembly (Final Sync)** (AC: #1, #2)
  - [x] Finalize the `submission_demo.ipynb` structure mapping `src/` modules to specific cells.
  - [x] Ensure all imports and classes are correctly ordered for a "Run All" execution.

## Dev Notes

- **Scenario Logic**: 
    - Danger signs should bypass HeAR/MedGemma.
    - Low-quality audio should trigger `Inconclusive` before MedGemma.
- **Visuals**: Use `NotebookRenderer.render(result)` for consistent card styling.
- **Latency**: Use `time.perf_counter()` for accurate millisecond tracking.
- **Resource Constraints**: The `@audit_resources` decorator from `src/utils/resource_audit.py` (Story 3.1) MUST be active.

### Project Structure Notes

- Development occurs in `src/` but is synchronized to `notebooks/submission_demo.ipynb`.
- Final artifact for submission is the `.ipynb` file.

### References

- [Architecture: Demo Story](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L80)
- [HeAR Encoder (Story 1.2)](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/1-2-hear-encoder-integration.md)
- [MedGemma Reasoning (Story 1.3)](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/1-3-medgemma-reasoning-engine.md)
- [Resource Audit (Story 3.1)](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/3-1-resource-telemetry-constraints.md)
- [Notebook Renderer (Story 3.2)](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/3-2-notebook-renderer-triage-cards.md)

## Dev Agent Record

### Agent Model Used

Antigravity (Gemini 2.5 Pro)

### Debug Log References

### Completion Notes List

- Implemented `LatencyTracker` for scenario performance metrics.
- Defined three clinical journeys: Success, Emergency, and Inconclusive.
- Assembled the full `submission_demo.ipynb` with all 10 architectural cells.
- Verified logic with unit tests and integration tests (all 62 tests passing).
- Fixed code review issues (Critical bugs in notebook runtime, API alignment).

### File List

- [src/utils/latency_tracker.py](file:///c:/AI2025/aura-med/src/utils/latency_tracker.py)
- [src/demo/scenarios.py](file:///c:/AI2025/aura-med/src/demo/scenarios.py)
- [src/demo/__init__.py](file:///c:/AI2025/aura-med/src/demo/__init__.py)
- [notebooks/submission_demo.ipynb](file:///c:/AI2025/aura-med/notebooks/submission_demo.ipynb)
- [tests/test_demo.py](file:///c:/AI2025/aura-med/tests/test_demo.py)
