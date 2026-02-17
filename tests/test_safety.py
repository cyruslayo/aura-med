import sys
from unittest.mock import MagicMock
import pytest
from src.datatypes import PatientVitals, DangerSignException
from src.agent.safety import SafetyGuard

def test_safety_guard_no_danger_signs():
    """Verify that SafetyGuard passes when no danger signs are present."""
    vitals = PatientVitals(age_months=12, respiratory_rate=40, danger_signs=False)
    # Should not raise any exception
    SafetyGuard.check(vitals)

def test_safety_guard_general_danger_sign_boolean():
    """Verify that SafetyGuard raises DangerSignException for generic boolean flag."""
    vitals = PatientVitals(age_months=12, respiratory_rate=40, danger_signs=True)
    with pytest.raises(DangerSignException) as excinfo:
        SafetyGuard.check(vitals)
    assert "Emergency Danger Signs Detected" in str(excinfo.value)

def test_safety_guard_specific_danger_signs():
    """
    Verify that specific danger signs trigger the exception with detailed messaging.
    """
    # Test cases for specific signs
    specific_signs = [
        "unable_to_drink",
        "vomits_everything",
        "convulsions",
        "lethargic"
    ]
    
    for sign in specific_signs:
        # We expect to be able to pass these in the constructor
        params = {
            "age_months": 12,
            "respiratory_rate": 40,
            sign: True
        }
        vitals = PatientVitals(**params)
        with pytest.raises(DangerSignException) as excinfo:
            SafetyGuard.check(vitals)
        assert "Emergency Danger Signs Detected" in str(excinfo.value)
        assert sign.replace("_", " ") in str(excinfo.value).lower()

def test_agent_bypasses_models_on_danger_signs():
    """Verify that AuraMedAgent doesn't call encoders/reasoners when danger signs exist."""
    from src.agent.core import AuraMedAgent
    
    mock_hear = MagicMock()
    mock_medgemma = MagicMock()
    
    agent = AuraMedAgent(hear_encoder=mock_hear, medgemma_reasoning=mock_medgemma)
    vitals = PatientVitals(age_months=12, respiratory_rate=45, convulsions=True)
    
    result = agent.predict("some/path.wav", vitals)
    
    # Verify result
    from src.datatypes import TriageStatus, DangerSignException
    assert result.status == TriageStatus.RED
    assert "Emergency Danger Signs Detected" in result.reasoning
    assert "convulsions" in result.reasoning.lower()
    
    # Verify bypass
    mock_hear.encode.assert_not_called()
    mock_medgemma.generate.assert_not_called()
