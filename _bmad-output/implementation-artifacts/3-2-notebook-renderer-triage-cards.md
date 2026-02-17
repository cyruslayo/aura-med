# Story 3.2: Notebook Renderer & Triage Cards

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a User,
I want to see a beautiful, mobile-style triage card,
so that I understand the result quickly and feel the "product quality".

## Acceptance Criteria

1. **Given** A `TriageResult` object (Red, Yellow, or Green)
2. **When** `NotebookRenderer.render()` is called
3. **Then** It returns an `IPython.display.HTML` object with inline CSS
4. **And** The card acts as a visual "Mobile Screen" in the notebook output (max-width: 400px, centered)
5. **And** It uses the correct color theme (Green/Yellow/Red) based on triage status
6. **And** It uses premium typography (Inter for headings, Roboto for body) via Google Fonts import
7. **And** It displays primary reasoning and recommended actions clearly (FR11, FR13, FR23)
8. **And** It includes a "Resource Telemetry" section showing RAM usage from `usage_stats`

## Tasks / Subtasks

- [x] **Task 1: Implement NotebookRenderer Class**
  - [x] Create `src/visualization/renderer.py`
  - [x] Implement `render_html` private method with CSS template
  - [x] Implement `render(result: TriageResult)` method returning `HTML`
- [x] **Task 2: Design CSS Template**
  - [x] Use a clean, mobile-inspired design (rounded corners, subtle shadows)
  - [x] Define color variables for Red/Yellow/Green states
  - [x] Include `@import` for Inter and Roboto fonts
- [x] **Task 3: Map TriageResult to View**
  - [x] Map `TriageResult.status` to CSS classes
  - [x] Extract reasoning and treatment recommendations from the result object
  - [x] Format resource telemetry into a small, elegant bar or badge
- [x] **Task 4: Integration Test in Notebook Context**
  - [x] Create `tests/test_renderer.py` to verify HTML generation
  - [x] Mock a `TriageResult` and verify strings for colors and fonts are present in output

## Dev Notes

- **Decouplication**: Ensure `NotebookRenderer` only depends on `TriageResult` (from `src/datatypes.py`).
- **CSS Strategy**: Use inline `<style>` within the returned HTML to ensure portability in Google Colab.
- **Mobile Fidelity**: Aim for a fixed-width container (e.g., `360px` or `400px`) with a white background and a distinct border to simulate a phone screen "card".
- **Color Palette**:
  - Green (Normal): `#2ECC71`
  - Yellow (Pneumonia/Caution): `#F1C40F`
  - Red (Severe/Danger): `#E74C3C`
- **Resource Stats**: Access `result.usage_stats['ram_gb']` and format as `X.X GB`.

### Project Structure Notes

- New file at `src/visualization/renderer.py` as per Architecture.
- Ensure common datatypes are used from `src/datatypes.py`.

### References

- [Architecture: Visualization Layer](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L108)
- [Epic 3.2 Requirements](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/epics.md#L237)
- [Resource Audio Audit Integration](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/3-1-resource-telemetry-constraints.md)

## Dev Agent Record

### Agent Model Used

Antigravity (Gemini 2.5 Pro)

### Completion Notes List

- Implemented `NotebookRenderer` class using `IPython.display.HTML`.
- Integrated Inter and Roboto fonts via Google Fonts.
- Added mobile-responsive CSS with specific color themes for each triage state (Green/Yellow/Red).
- Decoupled visualization from clinical logic by using `TriageResult` dataclass.
- Verified rendering with automated unit tests (including local environment mocks).
- **[Review Fixes]**: Added `html.escape` for XSS protection.
- **[Review Fixes]**: Created `src/visualization/__init__.py`.
- **[Review Fixes]**: Added accessibility fix for YELLOW status cards (dark text).
- **[Review Fixes]**: Corrected max-width to 400px per AC #4.
- **[Review Fixes]**: Significantly expanded test coverage for all status codes and XSS.

### File List

- [src/visualization/__init__.py](file:///c:/AI2025/aura-med/src/visualization/__init__.py)
- [src/visualization/renderer.py](file:///c:/AI2025/aura-med/src/visualization/renderer.py)
- [tests/test_renderer.py](file:///c:/AI2025/aura-med/tests/test_renderer.py)
