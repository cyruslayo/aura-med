"""
Unit tests for AuraMedAgent orchestrator.

Tests the pipeline orchestration logic using mocks for HeAREncoder
and MedGemmaReasoning to avoid loading heavy models.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import torch
import time

from src.agent.core import AuraMedAgent
from src.datatypes import PatientVitals, TriageResult, TriageStatus
from src.agent.safety import LowQualityError


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


class TestAuraMedAgentPredict:
    """Tests for AuraMedAgent.predict() orchestration."""
    
    @pytest.fixture
    def mock_encoder(self):
        """Create a mock HeAREncoder."""
        encoder = Mock()
        encoder.encode.return_value = torch.randn(1, 1024)
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
        return PatientVitals(age_months=18, respiratory_rate=40, danger_signs=False)
    
    def test_predict_calls_encoder_with_audio_path(self, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should call encoder.encode with the audio path."""
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        agent.predict("test/audio.wav", sample_vitals)
        
        mock_encoder.encode.assert_called_once_with("test/audio.wav")
    
    def test_predict_calls_reasoning_with_embedding_and_vitals(self, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should call reasoning.generate with embedding and vitals."""
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        agent.predict("test/audio.wav", sample_vitals)
        
        # Verify generate was called
        mock_reasoning.generate.assert_called_once()
        
        # Verify arguments: embedding tensor and vitals
        call_args = mock_reasoning.generate.call_args
        embedding_arg, vitals_arg = call_args[0]
        
        assert isinstance(embedding_arg, torch.Tensor)
        assert embedding_arg.shape == (1, 1024)
        assert vitals_arg is sample_vitals
    
    def test_predict_returns_triage_result(self, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should return a TriageResult object."""
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        result = agent.predict("test/audio.wav", sample_vitals)
        
        assert isinstance(result, TriageResult)
        assert result.status == TriageStatus.GREEN
        assert result.confidence == 0.9
    
    def test_predict_includes_latency_in_usage_stats(self, mock_encoder, mock_reasoning, sample_vitals):
        """Predict should record latency in usage_stats."""
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        result = agent.predict("test/audio.wav", sample_vitals)
        
        assert result.usage_stats is not None
        assert "latency_sec" in result.usage_stats
        assert "max_allowed_sec" in result.usage_stats
        assert result.usage_stats["latency_sec"] >= 0
        assert result.usage_stats["max_allowed_sec"] == 10.0
    
    def test_predict_orchestration_order(self, sample_vitals):
        """Predict should call encoder before reasoning (correct order)."""
        call_order = []
        
        mock_encoder = Mock()
        mock_encoder.encode.side_effect = lambda x: (call_order.append("encode"), torch.randn(1, 1024))[1]
        
        mock_reasoning = Mock()
        mock_reasoning.generate.side_effect = lambda e, v: (
            call_order.append("generate"),
            TriageResult(TriageStatus.GREEN, 0.9, "OK")
        )[1]
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        agent.predict("test/audio.wav", sample_vitals)
        
        assert call_order == ["encode", "generate"], "Encoder must be called before reasoning"


class TestAuraMedAgentErrorHandling:
    """Tests for error propagation in AuraMedAgent."""
    
    @pytest.fixture
    def sample_vitals(self):
        return PatientVitals(age_months=12, respiratory_rate=35)
    
    def test_predict_propagates_file_not_found_error(self, sample_vitals):
        """Predict should propagate FileNotFoundError from encoder."""
        mock_encoder = Mock()
        mock_encoder.encode.side_effect = FileNotFoundError("Audio file not found")
        mock_reasoning = Mock()
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            agent.predict("nonexistent.wav", sample_vitals)
    
    def test_predict_propagates_low_quality_error(self, sample_vitals):
        """Predict should propagate LowQualityError from encoder."""
        mock_encoder = Mock()
        mock_encoder.encode.side_effect = LowQualityError("Audio too short")
        mock_reasoning = Mock()
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        with pytest.raises(LowQualityError, match="Audio too short"):
            agent.predict("short_audio.wav", sample_vitals)
    
    def test_predict_propagates_reasoning_error(self, sample_vitals):
        """Predict should propagate errors from reasoning module."""
        mock_encoder = Mock()
        mock_encoder.encode.return_value = torch.randn(1, 1024)
        mock_reasoning = Mock()
        mock_reasoning.generate.side_effect = RuntimeError("Model inference failed")
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        
        with pytest.raises(RuntimeError, match="Model inference failed"):
            agent.predict("test.wav", sample_vitals)


class TestAuraMedAgentLatencyLogging:
    """Tests for latency tracking functionality."""
    
    @pytest.fixture
    def sample_vitals(self):
        return PatientVitals(age_months=24, respiratory_rate=30)
    
    def test_latency_is_positive(self, sample_vitals):
        """Latency should be a positive number."""
        mock_encoder = Mock()
        mock_encoder.encode.return_value = torch.randn(1, 1024)
        mock_reasoning = Mock()
        mock_reasoning.generate.return_value = TriageResult(TriageStatus.GREEN, 0.8, "OK")
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        result = agent.predict("test.wav", sample_vitals)
        
        assert result.usage_stats["latency_sec"] > 0
    
    def test_latency_reflects_processing_time(self, sample_vitals):
        """Latency should approximately reflect actual processing time."""
        delay_sec = 0.1
        
        mock_encoder = Mock()
        def slow_encode(path):
            time.sleep(delay_sec)
            return torch.randn(1, 1024)
        mock_encoder.encode.side_effect = slow_encode
        
        mock_reasoning = Mock()
        mock_reasoning.generate.return_value = TriageResult(TriageStatus.GREEN, 0.8, "OK")
        
        agent = AuraMedAgent(hear_encoder=mock_encoder, medgemma_reasoning=mock_reasoning)
        result = agent.predict("test.wav", sample_vitals)
        
        # Allow some tolerance for execution overhead
        assert result.usage_stats["latency_sec"] >= delay_sec
        assert result.usage_stats["latency_sec"] < delay_sec + 0.5  # Reasonable upper bound
