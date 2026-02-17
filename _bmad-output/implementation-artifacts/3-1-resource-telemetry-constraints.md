# Story 3.1: Resource Telemetry & Constraints

Status: done

## Story

As a judge,
I want to see that the system consumes <4GB RAM,
so that I know it is feasible for edge deployment on low-cost devices.

## Acceptance Criteria

1. **Given** An inference task is running
2. **When** The `@audit_resources` decorator wraps the execution
3. **Then** It estimates/measures RAM and FLOPs usage
4. **And** It logs "Simulated RAM: X.X GB" (via logger) to the console
5. **And** Raises `EdgeConstraintViolation` if usage exceeds 4GB (simulated or real) (FR24)

## Tasks / Subtasks

- [x] **Task 1: Implement Resource Audit Decorator** (AC: #2, #3, #5)
  - [x] Create `src/utils/resource_audit.py`.
  - [x] Implement `@audit_resources` using `psutil` for RAM monitoring.
  - [x] Implement `EdgeConstraintViolation` check against a 4.0GB threshold.
- [x] **Task 2: Implement FLOPs Estimation** (AC: #3)
  - [x] Add heuristic FLOPs estimation within the decorator based on latency.
- [x] **Task 3: Integrate with AuraMedAgent** (AC: #1, #4)
  - [x] Modify `src/agent/core.py` to apply `@audit_resources` to `predict`.
  - [x] Ensure `TriageResult.usage_stats` is populated.
- [x] **Task 4: Unit Testing & Validation** (AC: #1-5)
  - [x] Create `tests/test_audit.py` with 100% coverage of telemetry logic.

## Dev Agent Record

### Agent Model Used

Antigravity (Gemini 2.5 Pro)

### File List

- [src/utils/resource_audit.py](file:///c:/AI2025/aura-med/src/utils/resource_audit.py)
- [src/agent/core.py](file:///c:/AI2025/aura-med/src/agent/core.py)
- [src/datatypes.py](file:///c:/AI2025/aura-med/src/datatypes.py)
- [tests/test_audit.py](file:///c:/AI2025/aura-med/tests/test_audit.py)
- [tests/test_agent.py](file:///c:/AI2025/aura-med/tests/test_agent.py) (Modified for compatibility)

### Completion Notes

- Resolved decorator exception swallowing issue.
- Standardized `usage_stats` keys.
- Unified `MAX_RAM_GB` in `config.py`.
