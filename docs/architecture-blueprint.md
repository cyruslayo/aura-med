# Technical Specification: Aura-Med Multimodal Architecture ("The Blueprints")

## 1. System Overview

The **Aura-Med** architecture is a hybrid multimodal system that bridges a frozen bioacoustic encoder (**HeAR**) with a quantized large language model (**MedGemma 2B**). The system is designed for **asynchronous inference** on edge devices, where audio features and clinical text are fused via a learned projection layer.

---

## 2. Model Component Specifications

### 2.1 Acoustic Encoder: Google HeAR

* **Foundation:** Health Acoustic Representations (HeAR).
* **Input:** 16kHz mono-channel PCM audio (2-second segments).
* **Output:** 512-dimensional embedding vector ().
* **Status:** Frozen (No gradient updates during primary training).

### 2.2 The Reasoning Brain: MedGemma 2B

* **Foundation:** `google/medgemma-2b-it`.
* **Architecture:** Transformer Decoder (Gemma-based).
* **Hidden Dimension ():** 2048.
* **Quantization:** INT4-bit (via BitsAndBytes for training, LiteRT for deployment).
* **Context Window:** 8,192 tokens.

---

## 3. The Bridging Mechanism: Multimodal Projection Layer

To allow MedGemma to "interpret" HeAR embeddings, we implement a **Linear Projection Bottleneck**. This layer transforms the 512-dim acoustic vector into the 2048-dim space of MedGemma tokens.

### 3.1 Mathematical Mapping

Given a HeAR embedding , the projected "Virtual Token"  is calculated as:



Where:

* 
* 

### 3.2 Token Insertion Strategy

The projected vectors are treated as **Continuous Prompt Tokens**. They are prepended to the text embedding sequence before being fed into the MedGemma transformer blocks.

---

## 4. Data Flow & Inference Pipeline

### Step 1: Signal Pre-processing

* **Audio:** Resample to 16,000Hz, apply Peak Normalization, and silence removal.
* **Text:** Tokenize patient metadata (Age, Vitals) using the MedGemma SentencePiece tokenizer.

### Step 2: Feature Extraction

* Audio is passed through the **HeAR Encoder** to generate the  embedding.
* Text is passed through the **MedGemma Embedding Layer** to generate  tokens.

### Step 3: Fusion & Generation

* The Projection Layer maps .
* **Input Sequence:** `[Acoustic_Virtual_Token] + [Instruction_Tokens] + [Clinical_Vitals_Tokens]`.
* **Generation:** MedGemma performs Auto-regressive decoding to produce the WHO IMCI Triage Report.

---

## 5. Deployment & Edge Optimization

### 5.1 Hardware Constraints

* **Target RAM:** < 6GB Peak Usage.
* **Target Device:** Arm64-v8a (Android/Linux Tablets).

### 5.2 Optimization Pipeline

1. **Export:** Convert PyTorch `.pth` to ONNX.
2. **Compression:** Apply **Weight-Only Quantization (INT4)** to the MedGemma weights.
3. **Runtime:** Deploy via **Google AI Edge LiteRT** for hardware acceleration on mobile NPUs/GPUs.

---

## 6. API Interface Definition (Python Pseudo-code)

```python
class AuraMedAgent:
    def __init__(self, model_path):
        self.encoder = load_hear_model()
        self.projector = load_projection_layer()
        self.llm = load_quantized_medgemma()

    def triage(self, audio_data, vitals_dict):
        # 1. Audio Embedding
        audio_emb = self.encoder(audio_data) # [1, 512]
        
        # 2. Project to Gemma Space
        virtual_token = self.projector(audio_emb) # [1, 2048]
        
        # 3. Text Tokenization
        text_prompt = self.format_prompt(vitals_dict)
        text_embs = self.llm.embed(text_prompt) # [N, 2048]
        
        # 4. Concatenate and Generate
        full_input = torch.cat([virtual_token, text_embs], dim=0)
        report = self.llm.generate(full_input)
        
        return report

```

---

