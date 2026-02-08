# Story 1.3: MedGemma Reasoning Engine

Status: done

## Story

As a clinician,
I want the system to reason about the case using MedGemma 1.5,
so that I get a preliminary diagnosis based on the audio and vitals.

## Acceptance Criteria

1. **Given** A HeAR embedding (tensor) and structured `PatientVitals`
   **When** `MedGemmaReasoning.generate(embedding, vitals)` is called
   **Then** The system constructs a structured prompt including vitals and strict reasoning instructions.

2. **Given** The inference pipeline is running
   **When** The `ProjectionLayer` receives the HeAR embedding (1024-dim)
   **Then** It projects it to the MedGemma embedding dimension (e.g., 2048 or model specific) without error.

3. **Given** The prompt and projected embedding are ready
   **When** The MedGemma model (MedGemma 1.5 4B IT, INT4 quantized) processes them
   **Then** It generates a "Chain of Thought" reasoning string in the specified format.

4. **Given** The raw LLM output
   **When** The system parses the response
   **Then** It returns a structured `TriageResult` object containing:
   - `status` (Red/Yellow/Green/Inconclusive)
   - `confidence` (float 0.0-1.0)
   - `reasoning` (str)

5. **Given** A lack of GPU (e.g. during CI tests)
   **When** The code runs
   **Then** It gracefully falls back to a mock implementation or skipped test, preventing CI failure.

## Tasks / Subtasks

- [x] **Task 1: Define Data Structures** (AC: #1, #4)
  - [x] Create `src/datatypes.py`
  - [x] Implement `PatientVitals` dataclass (age, rr, danger_signs)
  - [x] Implement `TriageResult` dataclass with Enums for Status.

- [x] **Task 2: Implement Projection Layer** (AC: #2)
  - [x] Create `src/models/projection.py`
  - [x] Implement `ProjectionLayer` class (nn.Module, Linear/MLP)
  - [x] Ensure input/output shapes match HeAR (1024) -> Gemma (Hidden Dim)
  - [x] Use `PROJECTION_INPUT_DIM` from config

- [x] **Task 3: Implement MedGemma Reasoning Class** (AC: #1, #3)
  - [x] Update `src/models/medgemma.py`
  - [x] Implement `load_model()` using `bitsandbytes` config for INT4 quantization
  - [x] Use `google/medgemma-1.5-4b-it` (Hugging Face / Kaggle Models)
  - [x] Implement `generate(embedding, vitals)` method
  - [x] Construct prompt with template (System + User info)

- [x] **Task 4: Implement Output Parsing** (AC: #4)
  - [x] Add internal method to parse STATUS/CONFIDENCE/REASONING from LLM output
  - [x] Handle parsing errors (fallback to Inconclusive)
  - [x] Map output to `TriageResult`

- [ ] **Task 5: Sync to Notebook** (AC: #1-4)
  - [ ] Copy `ProjectionLayer` and `MedGemmaReasoning` to Cell 2/3
  - [ ] Verify imports and class ordering
  - **Note:** Blocked due to .ipynb edit restrictions. Manual sync required.

- [x] **Task 6: Write Unit Tests** (AC: #5)
  - [x] Create `tests/test_medgemma.py`
  - [x] Mock mode for demo/CI (no heavy weights)
  - [x] Verify Prompt Construction logic (string matching)
  - [x] Verify Output Parsing logic (with sample raw outputs)
  - [x] Verify Projection Layer shapes

## Dev Notes

- **Model ID**: `google/medgemma-1.5-4b-it`.
- **Note on Size**: This is a 4B parameter model.
- **Quantization**: Essential! Use `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)`.
- **HeAR Embedding Dim**: 1024.
- **Gemma Embedding Dim**: Check `config.hidden_size`.
- **Mocking Strategy**:
  - For `test_medgemma.py`, MUST mock `AutoModelForCausalLM` and `AutoTokenizer`. Do NOT download weights in unit tests.
  - Test the *logic* (prompting, parsing, reshaping) separate from the *heavy_weights*.

### Technical Requirements
- **Dependencies**: `transformers`, `bitsandbytes`, `accelerate` (ensure in `requirements.txt`).
- **Safety**: Do NOT put HF Token in code. Use `os.environ.get("HF_TOKEN")` or Kaggle Secrets.

### Architecture Patterns
- **Isolation**: `MedGemmaReasoning` should not know about `Audio` or `HeAREncoder` implementation, only the embedding tensor.
- **Data Flow**: `PatientVitals` -> `Prompt` -> `LLM` -> `TriageResult`.

### References
- [Architecture: MedGemma](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L45)
- [Architecture: Data Structures](file:///c:/AI2025/aura-med/_bmad-output/planning-artifacts/architecture.md#L141-L142)
- [MedGemma 1.5 HF](https://huggingface.co/google/medgemma-1.5-4b-it)

## Dev Agent Record

### Agent Model Used

Gemini 2.5 Pro

### Debug Log References

- Fixed confidence parsing in `_parse_response` method.
- Added projection shape tests.
- Updated requirements.txt with missing dependencies.

### Completion Notes List

- Story completed with all core ACs implemented.
- Notebook sync (Task 5) blocked due to `.ipynb` file edit restrictions - requires manual copy.

### File List

- src/datatypes.py
- src/models/projection.py
- src/models/medgemma.py
- src/models/__init__.py
- src/config.py
- tests/test_medgemma.py
- requirements.txt
