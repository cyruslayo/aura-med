# Story 2.3: WHO IMCI Protocol Logic

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a clinician,
I want the output to match exact WHO IMCI guidelines,
so I can trust the action plan is medically standard.

## Acceptance Criteria

1. **Given** A raw model classification or automated triage (e.g., fast breathing)
2. **When** The diagnostic result is formatted
3. **Then** It maps correctly to WHO Color Codes:
   - FAST BREATHING / PNEUMONIA -> **YELLOW**
   - NORMAL BREATHING / COUGH OR COLD -> **GREEN**
   - DANGER SIGNS / SEVERE PNEUMONIA -> **RED**
4. **And** Displays the correct treatment text exactly as per PRD:
   - **YELLOW**: "Administer oral Amoxicillin. Follow up in 48 hours."
   - **GREEN**: "Soothe throat, fluids, rest. No antibiotics needed."
   - **RED**: "Emergency Danger Signs Detected. Immediate referral."
5. **And** No non-standard or hallucinated treatments are suggested (FR9, FR10).

## Tasks / Subtasks

- [x] **Task 1: Centralize WHO IMCI Protocol Constants** (AC: #3, #4)
  - [x] Create or update a centralized service (e.g., `src/agent/protocols.py` or within `datatypes.py`) to hold the standard WHO strings and mappings.
  - [x] Avoid hardcoding these strings inside the MedGemma model class or the core Agent class multiple times.
- [x] **Task 2: Implement TriageResult Enrichment** (AC: #3, #4)
  - [x] Update `AuraMedAgent.predict` (or a helper) to automatically attach the correct `action_recommendation` based on the `status`.
  - [x] Ensure that even if the LLM fails to provide a recommendation, a standard one is applied based on the status code.
- [x] **Task 3: Align MedGemma Output Parsing** (AC: #5)
  - [x] Update `src/models/medgemma.py` to ensure it doesn't return ad-hoc treatment strings.
  - [x] Prioritize the "Reasoning" trace from the LLM but use the "Action" from the centralized protocol.
- [x] **Task 4: Unit Testing for Protocol Compliance** (AC: #1-5)
  - [x] Create `tests/test_protocols.py` or update `tests/test_agent.py`.
  - [x] Verify that every `status` (RED, YELLOW, GREEN) correctly maps to its PRD-mandated string.

## Dev Notes

### Architecture Intelligence
- **Separation of Concerns**: Keep the "Action Plan" logic separate from the "Reasoning" logic. Reasoning is AI-driven (probabilistic); Action Plan is Protocol-driven (deterministic).
- **Enforcement**: Use the `TriageStatus` Enum strictly.

### Implementation Patterns
- **Protocol Class**: Consider a `WHOIMCIProtocol` class with a static method `get_action(status: TriageStatus) -> str`.
- **Formatting**: The `action_recommendation` field in `TriageResult` should be the primary carrier for these strings.

### Previous Story Intelligence
- **Story 2.1 Learning**: The `SafetyGuard` already uses a hardcoded bypass for RED signals. Story 2.3 should ensure this message is aligned with the PRD ("Emergency Danger Signs Detected. Immediate referral.").
- **Story 2.2 Learning**: For `INCONCLUSIVE` status, the pattern is to return a helpful instruction for re-recording. Continue this pattern.

### References
- [PRD: Triage Result Format](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/prd.md#L259)
- [Architecture: Clinical Safety](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L57)
- [Source: Agent Core](file:///c:/AI2025/aura-med/src/agent/core.py)

## Dev Agent Record

### Agent Model Used
Gemini 2.5 Pro (Antigravity)

### Completion Notes List
- Centralized WHO IMCI protocols in `src/datatypes.py` to prevent AI hallucinations and resolve circular dependencies.
- Updated `AuraMedAgent.predict` to enforce standardized action recommendations for all triage statuses (RED, YELLOW, GREEN, INCONCLUSIVE).
- Verified implementation with a comprehensive test suite (24 tests passing).

### File List
- src/agent/core.py
- src/agent/protocols.py
- src/agent/__init__.py
- src/datatypes.py
- src/models/medgemma.py
- src/agent/safety.py
- src/config.py
- tests/test_protocols.py
- tests/test_agent.py
- tests/test_medgemma.py
- tests/test_safety.py
- tests/test_quality.py
- tests/conftest.py
