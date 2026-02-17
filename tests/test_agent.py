import pytest
from unittest.mock import Mock, MagicMock, patch
import time
import os
import sys

from src.agent.core import AuraMedAgent
from src.datatypes import PatientVitals, TriageResult, TriageStatus, LowQualityError, DangerSignException

# L3: Real torch import check (might be mocked)
import torch


@pytest.mark.skipif(torch is None, reason="torch not installed")
class TestAuraMedAgentInit:
    """Tests for AuraMedAgent initialization."""
    
    def test_init_with_injected_dependencies(self):
        """Agent should accept injected encoder and reasoning instances."""
        mock_encoder = Mock()
        mock_reasoning = Mock()
        
        agent = AuraMedAgent(
            hear_encoder=mock_encoder,
            medgemma_reasoning=mock_reasoning
        )
        
        assert agent.hear_encoder is mock_encoder
        assert agent.medgemma_reasoning is mock_reasoning
    
    @patch('src.agent.core.HeAREncoder')
    @patch('src.agent.core.MedGemmaReasoning')
    def test_init_creates_default_instances(self, mock_reasoning_cls, mock_encoder_cls):
        """Agent should create default instances when none provided."""
        mock_encoder_cls.return_value = Mock()
        mock_reasoning_cls.return_value = Mock()
        
        agent = AuraMedAgent()
        
        assert mock_encoder_cls.called
        assert mock_reasoning_cls.called


@pytest.mark.skipif(torch is None, reason="torch not installed")
class TestAuraMedAgentPredict:
    """Tests for AuraMedAgent.predict() orchestration."""
    
    @pytest.fixture
    def mock_encoder(self):
        """Create a mock HeAREncoder."""
        encoder = Mock()
        encoder.encode.return_value = torch.randn(1, 512)
        return encoder
    
    @pytest.fixture
    def mock_reasoning(self):
        """Create a mock MedGemmaReasoning."""
        reasoning = Mock()
        reasoning.generate.return_value = TriageResult(
            status=TriageStatus.GREEN,
            confidence=0.9,
            reasoning="No abnormalities detected."
        )
        return reasoning
    
    @pytest.fixture
    def sample_vitals(self):
        """Create sample patient vitals."""
        # danger_signs=False to pass SafetyGuard
        return PatientVitals(age_months=18, respiratory_rate=40, danger_signs=False)
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_calls_encoder_with_audio_path(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should call encoder.encode with the audio path."""
        mock_exists.return_value = True
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        agent.predict("test/audio.wav", sample_vitals)
        
        mock_encoder.encode.assert_called_once_with("test/audio.wav")
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_calls_reasoning_with_embedding_and_vitals(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should call reasoning.generate with embedding and vitals."""
        mock_exists.return_value = True
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        agent.predict("test/audio.wav", sample_vitals)
        
        # Verify generate was called
        mock_reasoning.generate.assert_called_once()
        
        # M1: Correctly unpack and verify args
        # call_args is (args, kwargs). args is (embedding, vitals)
        args, _ = mock_reasoning.generate.call_args
        embedding_arg, vitals_arg = args
        
        assert isinstance(embedding_arg, torch.Tensor)
        # We don't check shape strictly against the mock return to avoid "mock testing mock"
        # but we verify it is indeed a tensor passed through
        assert vitals_arg is sample_vitals
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_returns_triage_result(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should return a TriageResult object."""
        mock_exists.return_value = True
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        result = agent.predict("test/audio.wav", sample_vitals)
        
        assert isinstance(result, TriageResult)
        assert result.status == TriageStatus.GREEN
        assert result.confidence == 0.9
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_includes_latency_in_usage_stats(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should record latency in usage_stats."""
        mock_exists.return_value = True
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        # M4: Robust perf_counter mock using side_effect with a generator or lambda
        with patch('time.perf_counter', side_effect=lambda: 0.5):
            result = agent.predict("test/audio.wav", sample_vitals)
        
        assert result.usage_stats is not None
        assert "latency_sec" in result.usage_stats
        assert "max_allowed_sec" in result.usage_stats
        assert result.usage_stats["latency_sec"] >= 0
        assert result.usage_stats["max_allowed_sec"] == 10.0
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_orchestration_order(self, mock_exists, sample_vitals):
        """Predict should call encoder before reasoning (correct order)."""
        mock_exists.return_value = True
        call_order = []
        
        mock_encoder = Mock()
        mock_encoder.encode.side_effect = lambda x: (call_order.append("encode"), torch.randn(1, 512))[1]
        
        mock_reasoning = Mock()
        mock_reasoning.generate.side_effect = lambda e, v: (
            call_order.append("generate"),
            TriageResult(TriageStatus.GREEN, 0.9, "OK")
        )[1]
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        agent.predict("test/audio.wav", sample_vitals)
        
        assert call_order == ["encode", "generate"], "Encoder must be called before reasoning"

    @patch('src.agent.core.os.path.exists')
    def test_predict_safety_override(self, mock_exists, mock_encoder, mock_reasoning):
        """Predict should trigger RED status immediately if danger signs are present."""
        mock_exists.return_value = True
        danger_vitals = PatientVitals(age_months=12, respiratory_rate=40, danger_signs=True)
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        result = agent.predict("test.wav", danger_vitals)
        
        assert result.status == TriageStatus.RED
        assert "Danger Sign" in result.reasoning
        # Task 2: Check for standardized action recommendation
        assert result.action_recommendation == "Emergency Danger Signs Detected. Immediate referral."
        # Verify inference was NOT called
        mock_encoder.encode.assert_not_called()
        mock_reasoning.generate.assert_not_called()

    @patch('src.agent.core.os.path.exists')
    def test_predict_enriches_result_with_protocol_action(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should enrich valid inference results with WHO protocol actions."""
        mock_exists.return_value = True
        # Mock returns YELLOW but NO action recommendation
        mock_reasoning.generate.return_value = TriageResult(
            status=TriageStatus.YELLOW,
            confidence=0.8,
            reasoning="Fast breathing detected."
        )
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        result = agent.predict("test.wav", sample_vitals)
        
        assert result.status == TriageStatus.YELLOW
        # Task 2: Verify action recommendation was injected from protocol
        assert result.action_recommendation == "Administer oral Amoxicillin. Follow up in 48 hours."

    @patch('src.agent.core.os.path.exists')
    def test_predict_enriches_green_result(self, mock_exists, mock_encoder, mock_reasoning, sample_vitals):
        """M2: Predict should enrich GREEN results with standard WHO protocols."""
        mock_exists.return_value = True
        # Reasoning returns GREEN with NO action
        mock_reasoning.generate.return_value = TriageResult(
            status=TriageStatus.GREEN,
            confidence=0.9,
            reasoning="Normal breathing."
        )
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        result = agent.predict("test.wav", sample_vitals)
        
        assert result.status == TriageStatus.GREEN
        assert result.action_recommendation == "Soothe throat, fluids, rest. No antibiotics needed."


@pytest.mark.skipif(torch is None, reason="torch not installed")
class TestAuraMedAgentErrorHandling:
    """Tests for error propagation in AuraMedAgent."""
    
    @pytest.fixture
    def sample_vitals(self):
        return PatientVitals(age_months=12, respiratory_rate=35, danger_signs=False)
    
    @patch('src.agent.core.os.path.exists')
    def test_predict_raises_value_error_if_no_audio_path(self, mock_exists, sample_vitals):
        """Predict should raise ValueError if audio_path is empty."""
        agent = AuraMedAgent()
        with pytest.raises(ValueError, match="audio_path must be provided"):
            agent.predict("", sample_vitals)

    @patch('src.agent.core.os.path.exists')
    @patch('src.agent.core.HeAREncoder')
    @patch('src.agent.core.MedGemmaReasoning')
    def test_predict_raises_file_not_found(self, mock_reasoning, mock_encoder, mock_exists, sample_vitals):
        """Predict should raise FileNotFoundError if file doesn't exist."""
        mock_exists.return_value = False
        agent = AuraMedAgent()
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            agent.predict("nonexistent.wav", sample_vitals)

    @patch('src.agent.core.os.path.exists')
    @patch('src.agent.core.HeAREncoder')
    @patch('src.agent.core.MedGemmaReasoning')
    def test_predict_returns_inconclusive_on_low_quality_error(self, mock_reasoning, mock_encoder, mock_exists, sample_vitals):
        """H4: Predict should return INCONCLUSIVE on LowQualityError instead of crashing."""
        mock_exists.return_value = True
        mock_encoder_inst = mock_encoder.return_value
        mock_encoder_inst.encode.side_effect = LowQualityError("Audio too short")

        agent = AuraMedAgent()
        result = agent.predict("some_audio.wav", sample_vitals)

        assert result.status == TriageStatus.INCONCLUSIVE
        assert "Audio too short" in result.reasoning
        # Task 2: Check for standardized action recommendation
        assert "re-record" in result.action_recommendation.lower()
        mock_reasoning.return_value.generate.assert_not_called()
    
    @patch('src.agent.core.os.path.exists')
    @patch('src.agent.core.HeAREncoder')
    @patch('src.agent.core.MedGemmaReasoning')
    def test_predict_wraps_generic_errors(self, mock_reasoning, mock_encoder, mock_exists, sample_vitals):
        """H4: Predict should wrap generic errors with Agent context."""
        mock_exists.return_value = True
        mock_encoder_inst = mock_encoder.return_value
        mock_encoder_inst.encode.return_value = torch.randn(1, 512)
        mock_reasoning_inst = mock_reasoning.return_value
        mock_reasoning_inst.generate.side_effect = RuntimeError("Model inference failed")
        
        agent = AuraMedAgent()
        
        with pytest.raises(RuntimeError, match="AuraMedAgent: Pipeline execution failed"):
            agent.predict("test.wav", sample_vitals)


@pytest.mark.skipif(torch is None, reason="torch not installed")
class TestAuraMedAgentLatencyLogging:
    """Tests for latency tracking functionality."""
    
    @pytest.fixture
    def sample_vitals(self):
        return PatientVitals(age_months=24, respiratory_rate=30, danger_signs=False)
    
    @patch('src.agent.core.os.path.exists')
    def test_latency_is_positive(self, mock_exists, sample_vitals):
        """Latency should be a positive number."""
        mock_exists.return_value = True
        mock_encoder = Mock()
        mock_encoder.encode.return_value = torch.randn(1, 512)
        mock_reasoning = Mock()
        mock_reasoning.generate.return_value = TriageResult(TriageStatus.GREEN, 0.8, "OK")
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        with patch('time.perf_counter', side_effect=lambda: 0.1):
            result = agent.predict("test.wav", sample_vitals)
        
        assert result.usage_stats["latency_sec"] >= 0
    
    @patch('src.agent.core.os.path.exists')
    @patch('src.agent.core.logger')
    def test_latency_warning_on_threshold(self, mock_logger, mock_exists, sample_vitals):
        """M2: Predict should log a warning if latency exceeds threshold."""
        mock_exists.return_value = True
        mock_encoder = Mock()
        
        # Simulate >10s delay
        def slow_encode(path):
            # We wrap time.perf_counter instead of sleeping for 10s in a unit test
            return torch.randn(1, 512)
        
        mock_encoder.encode.side_effect = slow_encode
        mock_reasoning = Mock()
        mock_reasoning.generate.return_value = TriageResult(TriageStatus.GREEN, 0.8, "OK")
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        # Patch time.perf_counter to simulate 11 seconds
        with patch('time.perf_counter', side_effect=[0.0, 11.0, 11.0, 11.0, 11.0]):
            agent.predict("test.wav", sample_vitals)
            
        mock_logger.warning.assert_called()
        # Check if the warning message contains "exceeded threshold"
        args, _ = mock_logger.warning.call_args
        assert "exceeded threshold" in args[0]
