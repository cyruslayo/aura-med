import time
import logging
import os
from typing import Optional

from src.models.hear_encoder import HeAREncoder
from src.models.medgemma import MedGemmaReasoning
from src.agent.safety import SafetyGuard
from src.datatypes import PatientVitals, TriageResult, TriageStatus, DangerSignException, LowQualityError
from src.agent.protocols import WHOIMCIProtocol
from src.config import MAX_INFERENCE_TIME_SEC
from src.utils.resource_audit import audit_resources

logger = logging.getLogger(__name__)


class AuraMedAgent:
    """
    The main orchestrator for the AuraMed diagnostic pipeline.
    
    Encapsulates HeAREncoder and MedGemmaReasoning components,
    providing a single `predict()` interface for end-users.
    """
    
    def __init__(
        self,
        hear_encoder: Optional[HeAREncoder] = None,
        medgemma_reasoning: Optional[MedGemmaReasoning] = None
    ):
        """
        Initialize the AuraMedAgent.
        """
        self.hear_encoder = hear_encoder or HeAREncoder()
        self.medgemma_reasoning = medgemma_reasoning or MedGemmaReasoning()
        logger.info("AuraMedAgent initialized successfully.")

    def _finalize_result(self, result: TriageResult, start_time: float) -> TriageResult:
        """Calculate latency and attach usage stats to the result."""
        end_time = time.perf_counter()
        latency_sec = round(end_time - start_time, 3)
        
        # Initialize usage_stats if not present (decorator might have added it if order was different)
        if result.usage_stats is None:
            result.usage_stats = {}
            
        result.usage_stats.update({
            "latency_sec": latency_sec,
            "max_allowed_sec": MAX_INFERENCE_TIME_SEC
        })
        
        logger.info("Prediction complete. Status: %s, Latency: %.3fs", result.status.value, latency_sec)
        
        if latency_sec > MAX_INFERENCE_TIME_SEC:
            logger.warning(
                "Latency (%.2fs) exceeded threshold (%.2fs)",
                latency_sec, MAX_INFERENCE_TIME_SEC
            )
        return result

    @audit_resources
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
            ValueError: If inputs are invalid.
            FileNotFoundError: If the audio file doesn't exist.
            RuntimeError: If the pipeline fails with context.
        """
        start_time = time.perf_counter()
        
        # H1: Safety Check First (Architecture Mandate)
        if not isinstance(vitals, PatientVitals):
            raise ValueError("vitals must be an instance of PatientVitals")
            
        try:
            SafetyGuard.check(vitals)
        except DangerSignException as e:
            logger.warning("Safety Override Triggered: %s", str(e))
            result = TriageResult(
                status=TriageStatus.RED,
                confidence=1.0,
                reasoning=str(e),
                action_recommendation=WHOIMCIProtocol.get_action(TriageStatus.RED)
            )
            return self._finalize_result(result, start_time)

        # H2: Input Validation
        if not audio_path:
            raise ValueError("audio_path must be provided")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            # Step 1: Extract audio embeddings via HeAR
            logger.info("Processing audio file: %s", audio_path)
            embedding = self.hear_encoder.encode(audio_path)
            
            # Step 2: Generate clinical reasoning via MedGemma
            logger.info("Generating clinical reasoning for patient: age=%s mo, RR=%s", vitals.age_months, vitals.respiratory_rate)
            result = self.medgemma_reasoning.generate(embedding, vitals)
            
            # H5: Protocol Enforcement - Override/Enrich with standard WHO actions
            result.action_recommendation = WHOIMCIProtocol.get_action(result.status)
            
            return self._finalize_result(result, start_time)

        except LowQualityError as e:
            logger.warning("Audio Quality Error: %s", str(e))
            result = TriageResult(
                status=TriageStatus.INCONCLUSIVE,
                confidence=0.0,
                reasoning=f"Inconclusive: {str(e)}. Please re-record in a quieter environment.",
                action_recommendation=WHOIMCIProtocol.get_action(TriageStatus.INCONCLUSIVE)
            )
            return self._finalize_result(result, start_time)
        except Exception as e:
            # H4: Wrap generic errors with context
            logger.exception("Pipeline component failed")
            raise RuntimeError(f"AuraMedAgent: Pipeline execution failed: {str(e)}") from e
