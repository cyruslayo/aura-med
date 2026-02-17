import os
import numpy as np
import soundfile as sf
from src.datatypes import PatientVitals


class DemoScenarios:
    """Provides pre-configured scenarios for the end-to-end demo journeys."""
    
    DEFAULT_AUDIO = os.path.join("data", "test_sample.wav")

    @staticmethod
    def get_journey_1_success():
        """
        Scenario: 7-month old with fast breathing but no danger signs.
        Expected: YELLOW Triage (Pneumonia) -> Action: Oral Amoxicillin.
        """
        vitals = PatientVitals(
            age_months=7,
            respiratory_rate=52,  # > 50 is fast for 2-12 months
            danger_signs=False
        )
        return DemoScenarios.DEFAULT_AUDIO, vitals, "Journey 1: Clinical Success (Pneumonia)"

    @staticmethod
    def get_journey_2_emergency():
        """
        Scenario: Child presenting with lethargy.
        Expected: RED Triage (Emergency) -> Action: Urgent Referral.
        Bypasses AI model processing (safety guard override).
        """
        vitals = PatientVitals(
            age_months=24,
            respiratory_rate=30,
            danger_signs=True,
            lethargic=True
        )
        return DemoScenarios.DEFAULT_AUDIO, vitals, "Journey 2: Emergency Override (Lethargy)"

    @staticmethod
    def get_journey_3_inconclusive():
        """
        Scenario: Audio quality too low for reliable analysis.
        Expected: INCONCLUSIVE Triage -> Action: Re-record.
        
        Creates a near-silent WAV file that will trigger the noise gate
        (RMS below NOISE_RMS_LOWER_THRESHOLD).
        """
        vitals = PatientVitals(
            age_months=12,
            respiratory_rate=25,
            danger_signs=False
        )
        
        # Generate a real low-quality (near-silent) audio file
        low_quality_path = os.path.join("data", "low_quality_test.wav")
        DemoScenarios._create_silent_audio(low_quality_path)
        
        return low_quality_path, vitals, "Journey 3: Inconclusive (Low Quality Audio)"
    
    @staticmethod
    def _create_silent_audio(path: str, duration_sec: float = 3.0, sr: int = 16000):
        """
        Create a near-silent WAV file that will trigger the encoder's noise gate.
        
        The audio has extremely low amplitude (RMS < 0.001) to simulate
        a recording with no clear signal.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Near-zero amplitude noise (RMS ≈ 0.0001)
        samples = int(sr * duration_sec)
        silent_audio = np.random.normal(0, 0.00005, samples).astype(np.float32)
        sf.write(path, silent_audio, sr)
