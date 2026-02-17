import torch
import re
import logging
from src.config import MEDGEMMA_MODEL_PATH, IS_DEMO_MODE, HEAR_EMBEDDING_DIM
from src.datatypes import PatientVitals, TriageResult, TriageStatus
from src.agent.protocols import WHOIMCIProtocol

logger = logging.getLogger(__name__)


class MedGemmaReasoning:
    """
    MedGemma Reasoning Engine.
    
    Uses Google's MedGemma 4B-IT for clinical triage reasoning based on
    patient vitals and audio analysis from HeAR embeddings.
    
    Integration strategy: Text-Mediated Fusion (Option A)
    - HeAR embeddings are summarized as structured text features
    - Combined with patient vitals in a clinical prompt
    - MedGemma generates chain-of-thought reasoning and triage decision
    """
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.processor = None
        
        if not IS_DEMO_MODE:
            self.load_model()
        else:
            print(f"⚠️ MedGemma initialized in DEMO mode (no GPU). Using mock reasoning.")
            logger.info("MedGemma in DEMO/MOCK mode for: %s", MEDGEMMA_MODEL_PATH)

    def load_model(self):
        """Load MedGemma 4B-IT with quantization for edge-friendly inference."""
        try:
            from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig
            
            print(f"Loading MedGemma from {MEDGEMMA_MODEL_PATH}...")
            logger.info("Loading MedGemma from %s", MEDGEMMA_MODEL_PATH)
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            
            self.processor = AutoProcessor.from_pretrained(MEDGEMMA_MODEL_PATH)
            self.model = AutoModelForImageTextToText.from_pretrained(
                MEDGEMMA_MODEL_PATH,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
            )
            
            print(f"✅ MedGemma loaded successfully. Device: {self.device}")
            logger.info("MedGemma loaded successfully.")
            
        except ImportError as e:
            logger.error("Required package not installed: %s", str(e))
            print(f"⚠️ Missing dependency: {e}. Falling back to mock reasoning.")
        except Exception as e:
            logger.error("Failed to load MedGemma: %s", str(e))
            print(f"⚠️ MedGemma load failed: {e}. Falling back to mock reasoning.")

    def generate(self, embedding: torch.Tensor, vitals: PatientVitals) -> TriageResult:
        """
        Generate triage reasoning and status.
        
        Uses text-mediated fusion: HeAR embedding characteristics are described
        textually and combined with patient vitals in the clinical prompt.
        
        Args:
            embedding: (1, 512) tensor from HeAR encoder
            vitals: PatientVitals object with clinical data
            
        Returns:
            TriageResult with status, confidence, reasoning, and action
        """
        if self.model is None or self.processor is None:
            return self._mock_generate(vitals)

        # 1. Summarize audio embedding as text features
        audio_summary = self._summarize_embedding(embedding)
        
        # 2. Construct clinical prompt with audio + vitals
        prompt = self._construct_prompt(vitals, audio_summary)
        
        # 3. Format as chat messages for MedGemma
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": (
                    "You are a pediatric clinical decision support system following "
                    "WHO IMCI (Integrated Management of Childhood Illness) protocols. "
                    "You analyze acoustic cough analysis and patient vitals to provide "
                    "triage recommendations. You must be precise and evidence-based."
                )}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
        
        try:
            # 4. Tokenize with chat template
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            input_len = inputs["input_ids"].shape[-1]
            
            # 5. Generate response
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.2,
                    do_sample=True,
                )
            
            # 6. Decode only new tokens
            generated_tokens = outputs[0][input_len:]
            response = self.processor.decode(generated_tokens, skip_special_tokens=True)
            
            logger.info("MedGemma response length: %d chars", len(response))
            return self._parse_response(response)
            
        except Exception as e:
            logger.error("MedGemma inference error: %s", str(e))
            # Fallback to mock on runtime errors to avoid crashing the demo
            logger.warning("Falling back to mock reasoning due to inference error")
            return self._mock_generate(vitals)

    def _summarize_embedding(self, embedding: torch.Tensor) -> str:
        """
        Convert HeAR embedding into a textual summary for text-mediated fusion.
        
        Extracts statistical features from the embedding that may correlate
        with acoustic characteristics relevant to respiratory diagnosis.
        """
        if embedding is None:
            return "Audio embedding: unavailable"
        
        emb = embedding.squeeze().detach().cpu().numpy()
        
        # Extract meaningful statistical features
        emb_mean = float(emb.mean())
        emb_std = float(emb.std())
        emb_max = float(emb.max())
        emb_min = float(emb.min())
        emb_norm = float((emb ** 2).sum() ** 0.5)
        
        # Identify dominant feature dimensions (top activated)
        top_k = min(5, len(emb))
        top_indices = emb.argsort()[-top_k:][::-1]
        
        return (
            f"Acoustic cough analysis (HeAR bioacoustic embedding): "
            f"mean activation={emb_mean:.3f}, std={emb_std:.3f}, "
            f"range=[{emb_min:.3f}, {emb_max:.3f}], L2-norm={emb_norm:.3f}. "
            f"Top-{top_k} activated feature indices: {top_indices.tolist()}."
        )

    def _construct_prompt(self, vitals: PatientVitals, audio_summary: str = "") -> str:
        """Construct the clinical triage prompt with vitals and audio analysis."""
        
        # Determine respiratory rate classification per WHO IMCI
        if vitals.age_months < 2:
            fast_breathing_threshold = 60
        elif vitals.age_months < 12:
            fast_breathing_threshold = 50
        else:
            fast_breathing_threshold = 40
        
        rr_status = "fast breathing" if vitals.respiratory_rate >= fast_breathing_threshold else "normal"
        
        danger_signs_text = "None reported"
        if vitals.danger_sign_details:
            danger_signs_text = ", ".join(vitals.danger_sign_details.keys())
        
        return f"""Analyze the following pediatric patient data and provide a WHO IMCI triage assessment:

PATIENT DATA:
- Age: {vitals.age_months} months
- Respiratory Rate: {vitals.respiratory_rate} breaths/min (classified as: {rr_status}, threshold for age: {fast_breathing_threshold} bpm)
- Danger Signs: {danger_signs_text}

ACOUSTIC ANALYSIS:
{audio_summary}

Based on the WHO IMCI guidelines for respiratory illness triage, provide your assessment in this exact format:

REASONING: [Your step-by-step clinical reasoning considering both the acoustic analysis and patient vitals]
STATUS: [GREEN/YELLOW/RED]
CONFIDENCE: [0.0-1.0]"""

    def _parse_response(self, response: str) -> TriageResult:
        """Parse MedGemma's text response into a structured TriageResult."""
        
        # Parse status
        status = TriageStatus.INCONCLUSIVE
        if "STATUS: GREEN" in response.upper():
            status = TriageStatus.GREEN
        elif "STATUS: YELLOW" in response.upper():
            status = TriageStatus.YELLOW
        elif "STATUS: RED" in response.upper():
            status = TriageStatus.RED
        
        # Parse confidence
        confidence = 0.5  # Default if parsing fails
        confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", response, re.IGNORECASE)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        
        # Parse reasoning
        reasoning = ""
        upper_response = response.upper()
        if "REASONING:" in upper_response and "STATUS:" in upper_response:
            # Find the indices in the original response using the upper version
            reasoning_start = upper_response.index("REASONING:") + len("REASONING:")
            status_start = upper_response.index("STATUS:")
            reasoning = response[reasoning_start:status_start].strip()
            # Sanitize: remove any hallucinated treatment/action lines
            reasoning = re.sub(r"(?i)(Action|Treatment|Recommendation):\s*.*", "", reasoning).strip()
        elif "REASONING:" in upper_response:
            reasoning_start = upper_response.index("REASONING:") + len("REASONING:")
            reasoning = response[reasoning_start:].strip()
        else:
            # If no structured format, use the entire response as reasoning
            reasoning = response.strip()[:500]  # Cap at 500 chars
        
        if not reasoning:
            reasoning = "Model provided triage assessment."
        
        return TriageResult(
            status=status,
            confidence=confidence,
            reasoning=reasoning
        )

    def _mock_generate(self, vitals: PatientVitals) -> TriageResult:
        """Deterministic mock for demo/testing when no GPU is available."""
        if vitals.danger_signs:
            status = TriageStatus.RED
            reasoning = "Immediate referral required due to danger signs."
        elif vitals.respiratory_rate >= (50 if vitals.age_months < 12 else 40):
            status = TriageStatus.YELLOW
            reasoning = (
                f"Fast breathing detected ({vitals.respiratory_rate} bpm) "
                f"for {vitals.age_months}-month-old patient. "
                f"Consistent with pneumonia per WHO IMCI criteria."
            )
        else:
            status = TriageStatus.GREEN
            reasoning = (
                f"No fast breathing ({vitals.respiratory_rate} bpm, "
                f"threshold for age: {'50' if vitals.age_months < 12 else '40'} bpm) "
                f"or danger signs detected."
            )

        return TriageResult(
            status=status,
            confidence=1.0 if status == TriageStatus.RED else 0.85,
            reasoning=reasoning,
            action_recommendation=WHOIMCIProtocol.get_action(status)
        )
