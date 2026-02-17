# Story 2.2: Audio Quality Gate

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to know if my recording is too noisy or invalid,
so I can re-record instead of getting a wrong diagnosis.

## Acceptance Criteria

1. **Given** An audio file with high noise or low signal (e.g., shorter than 1s or mock noise > threshold)
2. **When** `HeAREncoder.encode()` processes the file
3. **Then** It raises a `LowQualityError`
4. **And** The `AuraMedAgent` catches this and returns an **INCONCLUSIVE** status
5. **And** The output reasoning advises "Please re-record in a quieter environment" (FR2, FR14, FR15, FR16)
6. **And** The LLM reasoning (MedGemma) is bypassed.

## Tasks / Subtasks

- [x] **Task 1: Enhance HeAREncoder with Quality Checks** (AC: #1, #3)
  - [x] Update `src/models/hear_encoder.py` to include a (mocked) noise detection logic.
  - [x] Ensure `LowQualityError` is raised with descriptive messages (too short, too noisy).
- [x] **Task 2: Refine Agent Handling** (AC: #4, #5, #6)
  - [x] Update `AuraMedAgent.predict` in `src/agent/core.py` to catch `LowQualityError`.
  - [x] Return a `TriageResult` with `TriageStatus.INCONCLUSIVE` and appropriate reasoning.
- [x] **Task 3: Unit Testing for Quality Gate** (AC: #1-6)
  - [x] Create `tests/test_quality.py`.
  - [x] Mock `HeAREncoder` to raise `LowQualityError` and verify `AuraMedAgent` behavior.
  - [x] Verify MedGemma is not called when quality is low.

## Dev Notes

### Architecture Intelligence
- **Graceful Failure**: Architecture mandates "Inconclusive is a valid return state, not an exception" at the Agent boundary.
- **Bypass Logic**: Similar to safety, quality issues should stop the pipeline before expensive LLM inference.

### Implementation Patterns
- **Error Types**: Use the existing `LowQualityError` and `LowConfidenceError` from `src/datatypes.py`.
- **Reasoning**: The `TriageResult.reasoning` should contain the user-facing instruction (re-record).

### Previous Story Intelligence
- **Story 2.1**: Established the pattern for `SafetyGuard` bypass. Follow a similar exception-catching pattern in `core.py`.
- **Source Sync**: Remember to sync any changes to the `AuraMedAgent` or `HeAREncoder` classes if they were already in the notebook (though they are currently being developed in `src/`).

### References
- [Architecture: Error Handling](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L106)
- [Epics: Story 2.2](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/epics.md#L191)
- [HeAR Encoder](file:///c:/AI2025/aura-med/src/models/hear_encoder.py)

## Dev Agent Record

### Agent Model Used

Gemini 2.5 Pro (Antigravity)

### Debug Log References

### Completion Notes List

- Enhanced `HeAREncoder` with `_detect_noise` functionality and duration checks.
- Implemented `LowQualityError` handling in `AuraMedAgent.predict()` to return `INCONCLUSIVE` status.
- Added 21 automated tests covering safety, quality, and orchestration.
- Verified that expensive model reasoning (MedGemma) is bypassed on low-quality audio.

### File List
- src/models/hear_encoder.py
- src/agent/core.py
- tests/test_quality.py
- tests/test_agent.py (updated)
