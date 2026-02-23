import torch
import re
import logging
from src.config import MEDGEMMA_MODEL_PATH, IS_DEMO_MODE, HEAR_EMBEDDING_DIM
from src.datatypes import PatientVitals, TriageResult, TriageStatus, get_fast_breathing_threshold, is_pediatric
from src.agent.protocols import WHORespiratoryProtocol
from src.models.projection import ProjectionLayer
from src.models.clinical_classifier import ClinicalClassifier

logger = logging.getLogger(__name__)


class MedGemmaReasoning:
    """
    MedGemma Reasoning Engine.
    
    Uses Google's MedGemma 1.5 4B-IT for clinical triage reasoning based on
    patient vitals and audio analysis from HeAR embeddings.
    
    Integration strategy: Text-Mediated Fusion (Option A)
    - HeAR embeddings are summarized as structured text features
    - Combined with patient vitals in a clinical prompt
    - MedGemma generates chain-of-thought reasoning and triage decision
    - Adheres to WHO IMCI (pediatric) and IMAI (adult) guidelines
    """
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.processor = None
        
        # Projection layer: bridges HeAR audio space → clinical feature space
        self.projection = ProjectionLayer(
            input_dim=HEAR_EMBEDDING_DIM,
            output_dim=2560
        )
        # Clinical Classifier: Trained linear probe for adventitious sounds
        self.classifier = ClinicalClassifier()
        
        if hasattr(self.projection, 'eval'):
            self.projection.eval()  # Inference-only (no training in demo)
        if hasattr(self.classifier, 'eval'):
            self.classifier.eval()
        
        if not IS_DEMO_MODE:
            self.load_model()
        else:
            print(f"⚠️ MedGemma initialized in DEMO mode (no GPU). Using mock reasoning.")
            logger.info("MedGemma in DEMO/MOCK mode for: %s", MEDGEMMA_MODEL_PATH)

    def load_model(self):
        """Load MedGemma 1.5 4B-IT with quantization for edge-friendly inference."""
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
                    "You are a clinical decision support system following "
                    "WHO respiratory triage protocols (IMCI for children, IMAI for adults). "
                    "You analyze acoustic cough analysis and patient vitals to provide "
                    "triage recommendations. You must be precise and evidence-based. "
                    "Always respond in the exact format: REASONING: ... STATUS: GREEN/YELLOW/RED CONFIDENCE: 0.0-1.0"
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
            
            # 5. Generate response (deterministic, no sampling)
            #    Use 2048 tokens to allow room for MedGemma's thinking + answer
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    do_sample=False,
                )
            
            # 6. Decode only new tokens
            generated_tokens = outputs[0][input_len:]
            response = self.processor.decode(generated_tokens, skip_special_tokens=True)
            
            # 7. Strip MedGemma 1.5 thinking tokens and internal reasoning
            response = re.sub(r'<unused\d+>', '', response)
            response = re.sub(r'^\s*thought\b', '', response, flags=re.IGNORECASE).strip()
            
            # 8. Extract only the clinical answer (skip thinking sections)
            #    MedGemma often emits planning text before REASONING:/STATUS:
            reasoning_idx = response.upper().find('REASONING:')
            if reasoning_idx > 0:
                response = response[reasoning_idx:]
            
            logger.info("MedGemma response length: %d chars", len(response))
            return self._parse_response(response)
            
        except Exception as e:
            logger.error("MedGemma inference error: %s", str(e))
            # Fallback to mock on runtime errors to avoid crashing the demo
            logger.warning("Falling back to mock reasoning due to inference error")
            return self._mock_generate(vitals)

    def _summarize_embedding(self, embedding: torch.Tensor) -> str:
        """Run through trained ClinicalClassifier to get semantic labels."""
        # Run through trained Linear Probe classifier
        label, description, confidence = self.classifier.predict(embedding)
        
        return (
            f"Acoustic cough analysis: {description} "
            f"(Classification confidence: {confidence:.0%})"
        )

    def _construct_prompt(self, vitals: PatientVitals, audio_summary: str = "") -> str:
        """Construct the clinical triage prompt with vitals and audio analysis."""
        
        # Determine respiratory rate classification based on age-adaptive thresholds
        fast_breathing_threshold = get_fast_breathing_threshold(vitals.age_months)
        
        rr_status = "fast breathing" if vitals.respiratory_rate >= fast_breathing_threshold else "normal"
        
        danger_signs_text = "None reported"
        if vitals.danger_sign_details:
            danger_signs_text = ", ".join(vitals.danger_sign_details.keys())
        
        # Handle age math for the LLM to prevent hallucination
        age_years = vitals.age_months // 12
        age_remaining = vitals.age_months % 12
        age_display = f"{vitals.age_months} months ({age_years} years, {age_remaining} months)"
        
        protocol_type = "WHO IMCI (Pediatric)" if is_pediatric(vitals.age_months) else "WHO IMAI (Adult/Adolescent)"

        return f"""Analyze the following patient data and provide a {protocol_type} triage assessment:

PATIENT DATA:
- Age: {age_display}{pediatric_note}
- Respiratory Rate: {vitals.respiratory_rate} breaths/min (classified as: {rr_status}, threshold for age: {fast_breathing_threshold} bpm)
- Danger Signs: {danger_signs_text}

ACOUSTIC ANALYSIS:
{audio_summary}

Based on the WHO IMCI guidelines for respiratory illness triage, provide your assessment in this exact format:

REASONING: [Your step-by-step clinical reasoning considering both the acoustic analysis and patient vitals]
STATUS: [Exactly one of: GREEN, YELLOW, or RED]
CONFIDENCE: [A number between 0.0 and 1.0]

Example of the expected output format:
REASONING: The patient shows fast breathing at 55 bpm (threshold 50 for age). Acoustic analysis reveals crackles. These findings are consistent with pathology per {protocol_type} guidelines.
STATUS: YELLOW
CONFIDENCE: 0.85"""

    def _parse_response(self, response: str) -> TriageResult:
        """Parse MedGemma's text response into a structured TriageResult.
        
        Uses multiple fallback strategies:
        1. Exact format match (STATUS: GREEN)
        2. Keyword search (green, yellow, red anywhere in response)
        3. Clinical keyword inference (pneumonia → YELLOW, danger → RED)
        """
        logger.debug("Raw MedGemma response: %s", response[:500])
        
        upper_response = response.upper()
        
        # --- Parse status (multi-strategy) ---
        status = TriageStatus.INCONCLUSIVE
        
        # Strategy 1: Exact format (STATUS: GREEN/YELLOW/RED)
        status_match = re.search(r'STATUS\s*:\s*(GREEN|YELLOW|RED)', upper_response)
        if status_match:
            status_str = status_match.group(1)
            status = {"GREEN": TriageStatus.GREEN, "YELLOW": TriageStatus.YELLOW, "RED": TriageStatus.RED}[status_str]
        else:
            # Strategy 2: Look for triage keywords anywhere in response
            # IMPORTANT: Use negative lookbehind to avoid false positives from
            # negated context like "no danger signs" or "absence of danger signs"
            red_patterns = [
                r'\bsevere pneumonia\b',
                r'(?<!\bNO )(?<!\bABSENCE OF )(?<!\bWITHOUT )\bDANGER SIGN',
                r'\brefer urgently\b',
                r'\bstatus\b.*\bred\b'
            ]
            yellow_patterns = [
                r'\bpneumonia\b', r'\bfast breathing\b', r'\bcrackles\b',
                r'\bwheezes?\b', r'\bcopd\b', r'\bbronchitis\b',
                r'\byellow\b.*\btriage\b', r'\bstatus\b.*\byellow\b'
            ]
            green_patterns = [
                r'\bcough or cold\b', r'\bno fast breathing\b',
                r'\bnormal\b.*\bbreathing\b', r'\bstatus\b.*\bgreen\b'
            ]
            
            if any(re.search(p, upper_response) for p in red_patterns):
                status = TriageStatus.RED
            elif any(re.search(p, upper_response) for p in yellow_patterns):
                status = TriageStatus.YELLOW
            elif any(re.search(p, upper_response) for p in green_patterns):
                status = TriageStatus.GREEN
        
        # --- Parse confidence ---
        confidence = 0.5  # Default if parsing fails
        confidence_match = re.search(r"CONFIDENCE\s*:\s*([\d.]+)", response, re.IGNORECASE)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass
        elif status != TriageStatus.INCONCLUSIVE:
            # If we successfully parsed a status but no confidence, assign reasonable default
            confidence = 0.75
        
        # --- Parse reasoning ---
        reasoning = ""
        if "REASONING:" in upper_response and "STATUS:" in upper_response:
            reasoning_start = upper_response.index("REASONING:") + len("REASONING:")
            status_start = upper_response.index("STATUS:")
            reasoning = response[reasoning_start:status_start].strip()
            reasoning = re.sub(r"(?i)(Action|Treatment|Recommendation):\s*.*", "", reasoning).strip()
        elif "REASONING:" in upper_response:
            reasoning_start = upper_response.index("REASONING:") + len("REASONING:")
            reasoning = response[reasoning_start:].strip()
        else:
            # Use entire response as reasoning (strip to 500 chars)
            reasoning = response.strip()[:500]
        
        if not reasoning:
            reasoning = "Model provided triage assessment."
        
        logger.info("Parsed triage: status=%s, confidence=%.2f", status.value, confidence)
        
        return TriageResult(
            status=status,
            confidence=confidence,
            reasoning=reasoning
        )

    def _mock_generate(self, vitals: PatientVitals) -> TriageResult:
        """Deterministic mock for demo/testing when no GPU is available."""
        threshold = get_fast_breathing_threshold(vitals.age_months)
        protocol = "IMCI" if is_pediatric(vitals.age_months) else "IMAI"
        
        if vitals.danger_signs:
            status = TriageStatus.RED
            reasoning = "Immediate referral required due to danger signs."
        elif vitals.respiratory_rate >= threshold:
            status = TriageStatus.YELLOW
            reasoning = (
                f"Fast breathing detected ({vitals.respiratory_rate} bpm) "
                f"for {vitals.age_months}-month-old patient (threshold: {threshold}). "
                f"Consistent with respiratory pathology per WHO {protocol} criteria."
            )
        else:
            status = TriageStatus.GREEN
            reasoning = (
                f"No fast breathing ({vitals.respiratory_rate} bpm, "
                f"threshold for age: {threshold} bpm) "
                f"or danger signs detected."
            )

        return TriageResult(
            status=status,
            confidence=1.0 if status == TriageStatus.RED else 0.85,
            reasoning=reasoning,
            action_recommendation=WHORespiratoryProtocol.get_action(status, vitals.age_months)
        )
