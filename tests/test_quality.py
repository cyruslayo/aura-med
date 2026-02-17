import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import torch
from src.models.hear_encoder import HeAREncoder
from src.agent.core import AuraMedAgent
from src.datatypes import PatientVitals, TriageStatus, LowQualityError

def test_hear_encoder_raises_low_quality_for_noisy_audio():
    """AC 1 & 3: HeAREncoder should raise LowQualityError if audio is too noisy."""
    encoder = HeAREncoder()
    with patch('src.models.hear_encoder.load_audio') as mock_load:
        # Create a "noisy" signal (simulated by high variance/amplitude)
        sr = 16000
        # uniform(-2, 2) has RMS roughly sqrt(4/3) = 1.15 > NOISE_RMS_UPPER_THRESHOLD
        noisy_audio = np.random.uniform(-2, 2, sr * 5)
        mock_load.return_value = (noisy_audio, sr)
        
        with pytest.raises(LowQualityError) as excinfo:
            encoder.encode("noisy.wav")
        assert "noisy" in str(excinfo.value).lower()

def test_hear_encoder_raises_low_quality_for_silent_audio():
    """H2: HeAREncoder should raise LowQualityError if audio is too silent."""
    encoder = HeAREncoder()
    with patch('src.models.hear_encoder.load_audio') as mock_load:
        sr = 16000
        # Silence (zeroes) has RMS 0 < NOISE_RMS_LOWER_THRESHOLD
        silent_audio = np.zeros(sr * 5)
        mock_load.return_value = (silent_audio, sr)
        
        with pytest.raises(LowQualityError) as excinfo:
            encoder.encode("silent.wav")
        assert "clear signal" in str(excinfo.value).lower()

def test_agent_returns_inconclusive_on_low_quality():
    """AC 4 & 5: Agent should catch LowQualityError and return INCONCLUSIVE."""
    mock_hear_inst = MagicMock()
    mock_medgemma = MagicMock()
    agent = AuraMedAgent(hear_encoder=mock_hear_inst, medgemma_reasoning=mock_medgemma)
    
    # Setup mock to raise LowQualityError
    mock_hear_inst.encode.side_effect = LowQualityError("Audio is too noisy")
    
    vitals = PatientVitals(age_months=24, respiratory_rate=35)
    
    with patch('os.path.exists', return_value=True):
        result = agent.predict("noisy.wav", vitals)
    
    assert result.status == TriageStatus.INCONCLUSIVE
    assert "re-record" in result.reasoning.lower()
    
    # AC 6: MedGemma should be bypassed
    mock_medgemma.generate.assert_not_called()
