import pytest
import os
from src.utils.latency_tracker import LatencyTracker
from src.demo.scenarios import DemoScenarios
from src.datatypes import PatientVitals, TriageStatus, TriageResult
from IPython.display import HTML

def test_latency_tracker_record():
    tracker = LatencyTracker()
    tracker.record("Test Scenario", TriageResult(
        status=TriageStatus.GREEN,
        confidence=1.0,
        reasoning="Test",
        usage_stats={"latency_sec": 1.234, "ram_gb": 0.5}
    ))
    
    assert len(tracker.metrics) == 1
    assert tracker.metrics[0]["Scenario"] == "Test Scenario"
    assert tracker.metrics[0]["Latency (s)"] == 1.234
    assert tracker.metrics[0]["RAM Usage (GB)"] == 0.5
    assert tracker.metrics[0]["Status"] == "GREEN"

def test_latency_tracker_summary_table():
    tracker = LatencyTracker()
    tracker.record("Success", TriageResult(
        status=TriageStatus.YELLOW,
        confidence=0.85,
        reasoning="Test",
        usage_stats={"latency_sec": 2.5, "ram_gb": 1.1}
    ))
    table = tracker.generate_summary_table()
    
    assert isinstance(table, HTML)
    assert "Success" in table.data
    assert "YELLOW" in table.data
    assert "Latency (s)" in table.data

def test_journey_1_success():
    audio, vitals, name = DemoScenarios.get_journey_1_success()
    assert "test_sample.wav" in audio
    assert isinstance(vitals, PatientVitals)
    assert vitals.age_months == 7
    assert vitals.danger_signs is False
    assert "Clinical Success" in name

def test_journey_2_emergency():
    audio, vitals, name = DemoScenarios.get_journey_2_emergency()
    assert "test_sample.wav" in audio
    assert vitals.danger_signs is True
    assert vitals.lethargic is True
    assert "Emergency" in name

from src.agent.core import AuraMedAgent

def test_integration_journey_1_success():
    agent = AuraMedAgent()
    audio, vitals, _ = DemoScenarios.get_journey_1_success()
    # Mock models are active, Journey 1 (age 7mo, RR 52) should result in YELLOW (Pneumonia)
    result = agent.predict(audio, vitals)
    assert result.status == TriageStatus.YELLOW
    assert "pneumonia" in result.reasoning.lower()
    assert result.usage_stats is not None
    assert "latency_sec" in result.usage_stats

def test_integration_journey_2_emergency():
    agent = AuraMedAgent()
    audio, vitals, _ = DemoScenarios.get_journey_2_emergency()
    # Journey 2 (lethargic=True) should trigger RED status via SafetyGuard
    result = agent.predict(audio, vitals)
    assert result.status == TriageStatus.RED
    assert "Emergency" in result.reasoning
    assert result.usage_stats is not None

def test_integration_journey_3_inconclusive():
    agent = AuraMedAgent()
    audio, vitals, _ = DemoScenarios.get_journey_3_inconclusive()
    # Journey 3 uses mocking path that should trigger INCONCLUSIVE
    # Note: Using the actual mock behavior of HeAREncoder in src/
    result = agent.predict(audio, vitals)
    assert result.status == TriageStatus.INCONCLUSIVE
    assert "Inconclusive" in result.reasoning or "Quality" in result.reasoning

def test_latency_tracker_with_triage_result():
    tracker = LatencyTracker()
    result = TriageResult(
        status=TriageStatus.GREEN,
        confidence=0.9,
        reasoning="Test",
        usage_stats={"latency_sec": 0.5, "ram_gb": 1.2}
    )
    tracker.record("Integration Scenario", result)
    assert len(tracker.metrics) == 1
    assert tracker.metrics[0]["Latency (s)"] == 0.5
    assert tracker.metrics[0]["RAM Usage (GB)"] == 1.2

