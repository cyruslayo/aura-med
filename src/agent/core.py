"""
AuraMed Agent - Core Orchestrator

This module implements the main AuraMedAgent class that orchestrates
the entire diagnostic pipeline: Audio -> HeAR -> MedGemma -> TriageResult.
"""
import time
import logging
from typing import Optional

from src.models.hear_encoder import HeAREncoder
from src.models.medgemma import MedGemmaReasoning
from src.datatypes import PatientVitals, TriageResult, TriageStatus
from src.config import MAX_INFERENCE_TIME_SEC

logger = logging.getLogger(__name__)


class AuraMedAgent:
    """
    The main orchestrator for the AuraMed diagnostic pipeline.
    
    Encapsulates HeAREncoder and MedGemmaReasoning components,
    providing a single `predict()` interface for end-users.
    
    Usage:
        agent = AuraMedAgent()
        vitals = PatientVitals(age_months=18, respiratory_rate=45)
        result = agent.predict("path/to/cough.wav", vitals)
    """
    
    def __init__(
        self,
        hear_encoder: Optional[HeAREncoder] = None,
        medgemma_reasoning: Optional[MedGemmaReasoning] = None
    ):
        """
        Initialize the AuraMedAgent.
        
        Args:
            hear_encoder: Optional HeAREncoder instance. Created internally if not provided.
            medgemma_reasoning: Optional MedGemmaReasoning instance. Created internally if not provided.
        """
        self.hear_encoder = hear_encoder or HeAREncoder()
        self.medgemma_reasoning = medgemma_reasoning or MedGemmaReasoning()
        logger.info("AuraMedAgent initialized successfully.")
    
    def predict(self, audio_path: str, vitals: PatientVitals) -> TriageResult:
        """
        Run the full diagnostic pipeline.
        
        Orchestrates: Audio -> HeAR Encoder -> MedGemma Reasoning -> TriageResult.
        
        Args:
            audio_path: Path to the audio file (.wav) containing cough recording.
            vitals: Patient vitals including age, respiratory rate, and danger signs.
            
        Returns:
            TriageResult: The structured triage outcome.
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            LowQualityError: If the audio is below quality threshold.
            ValueError: If vitals are invalid.
        """
        start_time = time.perf_counter()
        
        # Step 1: Extract audio embeddings via HeAR
        logger.info(f"Processing audio file: {audio_path}")
        embedding = self.hear_encoder.encode(audio_path)
        
        # Step 2: Generate clinical reasoning via MedGemma
        logger.info(f"Generating clinical reasoning for patient: age={vitals.age_months}mo, RR={vitals.respiratory_rate}")
        result = self.medgemma_reasoning.generate(embedding, vitals)
        
        # Step 3: Calculate and log latency
        end_time = time.perf_counter()
        latency_sec = end_time - start_time
        
        # Attach usage stats to result
        result.usage_stats = {
            "latency_sec": round(latency_sec, 3),
            "max_allowed_sec": MAX_INFERENCE_TIME_SEC
        }
        
        logger.info(f"Prediction complete. Status: {result.status.value}, Latency: {latency_sec:.3f}s")
        
        # Log warning if latency exceeded threshold
        if latency_sec > MAX_INFERENCE_TIME_SEC:
            logger.warning(
                f"Latency ({latency_sec:.2f}s) exceeded threshold ({MAX_INFERENCE_TIME_SEC}s)"
            )
        
        return result
