# Story 2.1: Safety & Danger Sign Overrides

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a safety officer,
I want the system to immediately flag danger signs (e.g., lethargy, convulsions),
so that critical cases are never missed by the AI.

## Acceptance Criteria

1. **Given** A patient input with `danger_signs=True` (or specific list in `PatientVitals`)
2. **When** `SafetyGuard.check()` is called OR `Agent.predict()` is run
3. **Then** The system returns a **RED ALERT** status IMMEDIATELY
4. **And** The LLM inference (MedGemma) and Audio processing (HeAR) are bypassed
5. **And** The reasoning explicitly states "Emergency Danger Signs Detected! Immediate referral required." (FR6, FR17)

## Tasks / Subtasks

- [x] **Task 1: Define Danger Sign Vocabulary** (AC: #1, #5)
  - [x] Update `src/datatypes.py` (if needed) to include list of specific danger signs if `danger_signs` becomes more than a boolean.
  - [x] Ensure `PatientVitals` can represent these signs clearly.
- [x] **Task 2: Implement Robust SafetyGuard Logic** (AC: #2, #3, #5)
  - [x] Enhance `src/agent/safety.py` to handle the specific logic for overrides.
  - [x] Ensure it raises `DangerSignException` with the correct medical messaging.
- [x] **Task 3: Refine Agent Integration** (AC: #4)
  - [x] Ensure `src/agent/core.py` catches `DangerSignException` and returns the `RED` status result without calling `HeAREncoder` or `MedGemmaReasoning`.
- [x] **Task 4: Unit Testing** (AC: #1-5)
  - [x] Create `tests/test_safety.py` or update `tests/test_agent.py`.
  - [x] Verify that when danger signs are present, mocks for models are NEVER called.
  - [x] Verify the specific "Emergency" reasoning message.

## Dev Notes

### Architecture Intelligence
- **Hard-Coded Logic Gate**: Architecture mandates that this bypass is deterministic and not based on AI performance.
- **Fail-Fast**: Safety check must be the first step in the `predict` pipeline.
- **Resource Audit**: While bypassed, resource telemetry should still log the minimal usage (or zero for models).

### Implementation Patterns
- **Naming**: Safety variables should be prefixed with `safety_` if adding internal state, but mostly focus on `vitals.danger_signs`.
- **Encapsulation**: `SafetyGuard` in `src/agent/safety.py` is the source of truth for protocol logic.

### Previous Story Intelligence
- **Consistency**: Story 1.4 established the `AuraMedAgent` orchestrator. Maintain the composition pattern where models are passed to the agent.
- **Learning**: Today's review of 1.4 revealed a basic implementation already exists; this story formalizes and hardens it against the full PRD requirements.

### References
- [Architecture: Deterministic Safety Overrides](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L93)
- [PRD: Model Safety](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/prd.md#L177)
- [Epics: Story 2.1](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/epics.md#L177)

## Dev Agent Record

### Agent Model Used
Gemini 2.5 Pro (Antigravity)

### Code Review Record
- **Review Date**: 2026-02-10
- **Issues Found**: 8 (Resolved)
- **Fixes Applied**:
  - Restored clean exception propagation for `ValueError` and `FileNotFoundError`.
  - Refactored `SafetyGuard` to use DRY field iteration from `PatientVitals`.
  - Broken circular import by moving exceptions to `src/datatypes.py`.
  - Standardized mock infrastructure via `tests/conftest.py`.

### Completion Notes List
- Defined granular danger sign vocabulary in `PatientVitals` (Task 1).
- Implemented robust `SafetyGuard` logic with specific WHO IMCI identifiers (Task 2).
- Updated `AuraMedAgent` to perform safety check as the very first action, ensuring maximum bypass efficiency (Task 3).
- Added comprehensive unit and integration tests in `tests/test_safety.py` (Task 4).

### File List
- src/agent/safety.py
- src/agent/core.py
- src/datatypes.py
- tests/test_safety.py
