import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from src.config import MEDGEMMA_MODEL_PATH, IS_DEMO_MODE
from src.datatypes import PatientVitals, TriageResult, TriageStatus
from src.models.projection import ProjectionLayer

class MedGemmaReasoning:
    """
    MedGemma 1.5 Reasoning Engine.
    Handles prompted inference with audio embeddings and vitals.
    """
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model = None
        self.tokenizer = None
        self.projection = None
        
        if not IS_DEMO_MODE:
            self.load_model()
        else:
            print(f"Initializing MedGemma in DEMO/MOCK mode for: {MEDGEMMA_MODEL_PATH}")
            # In demo mode, we still initialize the projection layer to verify shapes
            self.projection = ProjectionLayer(input_dim=1024, output_dim=2560).to(self.device)

    def load_model(self):
        """Load MedGemma 1.5 with 4-bit quantization."""
        print(f"Loading MedGemma 1.5 from {MEDGEMMA_MODEL_PATH}...")
        
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(MEDGEMMA_MODEL_PATH)
        self.model = AutoModelForCausalLM.from_pretrained(
            MEDGEMMA_MODEL_PATH,
            quantization_config=quantization_config,
            device_map="auto"
        )
        
        # Hidden size might vary, adjust projection accordingly
        hidden_size = self.model.config.hidden_size
        self.projection = ProjectionLayer(input_dim=1024, output_dim=hidden_size).to(self.device)
        print(f"Model loaded. Hidden size: {hidden_size}")

    def generate(self, embedding: torch.Tensor, vitals: PatientVitals) -> TriageResult:
        """
        Generate triage reasoning and status.
        
        Args:
            embedding: (1, 1024) tensor from HeAR
            vitals: PatientVitals object
        """
        if IS_DEMO_MODE:
            return self._mock_generate(vitals)

        # 1. Project embedding to LLM space
        projected_embeds = self.projection(embedding.to(self.device))
        
        # 2. Construct Prompt
        prompt = self._construct_prompt(vitals)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # 3. Combine embeds (This is a simplified multi-modal approach)
        # In a real MedGemma 1.5 workflow, embeddings might be interleaved.
        # Here we prioritize the text prompt + vitals.
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.2,
                do_sample=True
            )
            
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self._parse_response(response)

    def _construct_prompt(self, vitals: PatientVitals) -> str:
        return f"""<start_of_turn>user
You are a pediatric clinical assistant following WHO IMCI protocols.
Analyze the following patient data:
- Age: {vitals.age_months} months
- Respiratory Rate: {vitals.respiratory_rate} breaths/min
- Danger Signs: {"Yes" if vitals.danger_signs else "No"}

Based on the clinical findings and the acoustic cough analysis (provided via cross-modal embedding), 
provide a reasoning trace and a final triage status (GREEN, YELLOW, RED).

Format your response as:
REASONING: [Your clinical reasoning]
STATUS: [GREEN/YELLOW/RED]
CONFIDENCE: [0.0-1.0]<end_of_turn>
<start_of_turn>model
<ctrl94>thought
"""

    def _parse_response(self, response: str) -> TriageResult:
        import re
        # Parse status
        status = TriageStatus.INCONCLUSIVE
        if "STATUS: GREEN" in response: status = TriageStatus.GREEN
        elif "STATUS: YELLOW" in response: status = TriageStatus.YELLOW
        elif "STATUS: RED" in response: status = TriageStatus.RED
        
        # Parse confidence
        confidence = 0.5  # Default if parsing fails
        confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", response)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            except ValueError:
                pass
        
        # Parse reasoning
        reasoning = ""
        if "REASONING:" in response and "STATUS:" in response:
            reasoning = response.split("REASONING:")[-1].split("STATUS:")[0].strip()
        
        return TriageResult(
            status=status,
            confidence=confidence,
            reasoning=reasoning
        )

    def _mock_generate(self, vitals: PatientVitals) -> TriageResult:
        """Deterministic mock for demo purposes."""
        if vitals.danger_signs:
            return TriageResult(TriageStatus.RED, 1.0, "Immediate referral required due to danger signs.", action_recommendation="Refer URGENTLY to hospital.")
        
        if vitals.respiratory_rate > 50:
            return TriageResult(TriageStatus.YELLOW, 0.85, "Fast breathing detected for age. Consistent with pneumonia.", action_recommendation="Give oral Amoxicillin.")
            
        return TriageResult(TriageStatus.GREEN, 0.9, "No fast breathing or danger signs detected.", action_recommendation="Home care and follow-up if worsening.")
