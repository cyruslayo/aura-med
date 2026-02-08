# Story 1.2: HeAR Encoder Integration

Status: done

## Story

As a data scientist,
I want to extract embeddings from audio using HeAR,
So that we have a rich acoustic representation for analysis.

## Acceptance Criteria

1. **Given** A path to a valid .wav file (cough recording)
   **When** `HeAREncoder.encode(audio_path)` is called
   **Then** The audio is loaded using librosa and resampled to 16kHz

2. **Given** An audio file loaded into memory
   **When** Embedding extraction is performed
   **Then** A tensor of shape `(1, 1024)` (or model-specific dimension) is returned

3. **Given** An audio file longer than 10 seconds
   **When** `HeAREncoder.encode(audio_path)` is called
   **Then** The file is truncated to 10 seconds (or padded if shorter)

4. **Given** The HeAR model is being loaded
   **When** Mock mode is active (for testing)
   **Then** The mock returns deterministic embeddings without requiring real model weights

## Tasks / Subtasks

- [x] **Task 1: Implement Audio Loading Module** (AC: #1)
  - [x] Create `src/utils/audio.py` with `load_audio(path, sr=16000)` function
  - [x] Use librosa for audio loading with resampling to 16kHz
  - [x] Add proper error handling for missing/corrupt files
  - [x] Add type hints and docstrings

- [x] **Task 2: Implement Audio Preprocessing** (AC: #3)
  - [x] Add `normalize_duration(audio, target_length, sr)` function
  - [x] Truncate audio longer than 10s, pad shorter audio with zeros
  - [x] Return normalized waveform as numpy array

- [x] **Task 3: Upgrade HeAREncoder with Real Audio Processing** (AC: #1, #2)
  - [x] Update `src/models/hear_encoder.py` to use audio loading utilities
  - [x] Replace stub `encode()` with actual audio preprocessing pipeline
  - [x] Maintain mock model inference (actual HeAR weights loaded in later story)
  - [x] Return tensor shape `(1, 1024)` from processed audio

- [x] **Task 4: Add Audio Quality Validation** (AC: #1)
  - [x] Validate audio file exists and is readable
  - [x] Validate audio has sufficient duration (minimum 1 second)
  - [x] Raise appropriate exceptions for invalid inputs

- [x] **Task 5: Sync to Notebook** (AC: #1, #2, #3)
  - [x] Copy `audio.py` utilities to appropriate notebook cell
  - [x] Update Cell 2 with new `HeAREncoder` implementation
  - [x] Ensure notebook cells remain self-contained (no src imports)

- [x] **Task 6: Write Unit Tests** (AC: #1, #2, #3, #4)
  - [x] Create `tests/test_audio.py` for audio loading/preprocessing
  - [x] Update `tests/test_models.py` with real audio path tests
  - [x] Mock librosa in tests (continue mock pattern from Story 1.1)
  - [x] Test truncation and padding logic

- [x] **Task 7: Integration Test with Sample Audio** (AC: #1, #2, #3)
  - [x] Add sample test audio file to `data/` directory
  - [x] Verify end-to-end flow: file -> load -> preprocess -> encode
  - [x] Verify output tensor shape and type

## Dev Notes

### Architecture Patterns & Constraints

- **Hybrid Repo Strategy**: Develop in `src/`, sync to `submission_demo.ipynb`
- **Cell Discipline**: Imports at top of cell, no global state mutation
- **Error Handling**: Invalid audio should not crash; return error state gracefully
- **Naming Conventions**:
  - Functions: `snake_case` (e.g., `load_audio`, `normalize_duration`)
  - Classes: `PascalCase` (e.g., `HeAREncoder`)
  - Constants: `UPPER_SNAKE_CASE`

### Technical Stack

| Library | Purpose | Notes |
|---------|---------|-------|
| **librosa** | Audio I/O | Already in requirements.txt |
| **numpy** | Array manipulation | For waveform handling |
| **torch** | Tensor output | As established in Story 1.1 |

### Critical Implementation Details

> [!IMPORTANT]
> HeAR expects 16kHz mono audio. All input must be resampled.

> [!IMPORTANT]
> The actual HeAR model weights are NOT loaded in this story. We implement the preprocessing pipeline and mock the final embedding output. Real model loading will occur in a future story.

### Audio Processing Pipeline

```
.wav file -> librosa.load(sr=16000) -> normalize_duration(10s) -> HeAREncoder.encode() -> Tensor(1, 1024)
```

### Project Structure Notes

New file to create:
```
src/
├── utils/
│   ├── __init__.py          # Update with exports
│   └── audio.py             # NEW: Audio loading utilities
```

Files to modify:
- `src/models/hear_encoder.py` (upgrade from stub)
- `notebooks/submission_demo.ipynb` (Cell 2)

### Previous Story Learnings (from 1-1)

1. **Mock Pattern**: Use `tests/mocks/` for simulating heavy dependencies (torch, librosa)
2. **Init Files**: Always create `__init__.py` files for new packages
3. **Notebook Sync**: Copy full class code into notebook cells; no src imports
4. **Test Organization**: Match test file names to source files (`test_audio.py` for `audio.py`)

### References

- [Architecture: HeAR Encoder](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L78)
- [Architecture: Data Flow](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L209-L216)
- [Architecture: Project Structure](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L154-L179)
- [Epics: Story 1.2](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/epics.md#L131-L144)
- [PRD: FR1, FR3](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/prd.md)
- [Previous Story: 1-1](file:///c:/AI2025/aura-med/_bmad-output/implementation-artifacts/1-1-project-skeleton-model-loading.md)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Pro Experimental

### Debug Log References

- Verified `src/utils/audio.py` with `tests/test_audio.py` (unittest).
- Verified `HeAREncoder` integration with `tests/test_models.py`.
- Mocked `librosa` and `torch` to maintain environment independence.
- Verified 16kHz resampling and 10s duration normalization (truncation/padding).
- Verified minimum 1s duration validation.

### Completion Notes List

- Implemented `load_audio` and `normalize_duration` in `src/utils/audio.py`.
- Added `LowQualityError` to `src/agent/safety.py`.
- Upgraded `HeAREncoder` in `src/models/hear_encoder.py` to use preprocessing pipeline.
- Updated all relevant unit tests to support new pipeline requirements.

### File List

- src/utils/audio.py
- src/utils/__init__.py
- src/models/hear_encoder.py
- src/agent/safety.py
- tests/test_audio.py
- tests/test_models.py
- tests/mocks/librosa.py
- data/test_sample.wav
