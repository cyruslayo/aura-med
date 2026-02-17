import pytest
import psutil
from src.utils.resource_audit import audit_resources, MAX_RAM_GB
from src.datatypes import EdgeConstraintViolation, TriageResult, TriageStatus

# Mock result class to test usage_stats injection
class MockResult:
    def __init__(self):
        self.usage_stats = None

@audit_resources
def dummy_inference(should_succeed=True):
    if not should_succeed:
        # Simulate high memory usage by creating a large object
        _ = bytearray(int(100 * 1024**2)) # 100MB
    return MockResult()

@audit_resources
def error_inference():
    raise ValueError("Original Error")

class MockAgent:
    @audit_resources
    def predict(self):
        return MockResult()

def test_audit_resources_success(capsys):
    """Test that the decorator succeeds and logs for normal usage."""
    # M1: Now it uses logger, so we might need to check logs, but we kept logger config default
    # If using caplog instead of capsys for logger:
    result = dummy_inference(should_succeed=True)
    
    # Check usage stats enrichment
    assert result.usage_stats is not None
    assert "ram_gb" in result.usage_stats
    assert "flops_g" in result.usage_stats
    assert "latency_sec" in result.usage_stats

def test_audit_resources_violation(monkeypatch):
    """Test that EdgeConstraintViolation is raised when RAM limit is exceeded."""
    import src.utils.resource_audit as audit_mod
    monkeypatch.setattr(audit_mod, "MAX_RAM_GB", 0.0001)
    
    with pytest.raises(EdgeConstraintViolation) as excinfo:
        dummy_inference(should_succeed=True)
    assert "exceeds limit" in str(excinfo.value)

def test_audit_resources_latency():
    """Test that latency is measured even for very fast functions."""
    import time
    
    @audit_resources
    def fast_func():
        time.sleep(0.1)
        return MockResult()
    
    result = fast_func()
    assert result.usage_stats["latency_sec"] >= 0.09

def test_audit_resources_exception_propagation():
    """M2: Verify that original exceptions are NOT swallowed by the decorator."""
    with pytest.raises(ValueError, match="Original Error"):
        error_inference()

def test_audit_resources_on_method():
    """M4: Verify decorator works on class methods (handles 'self')."""
    agent = MockAgent()
    result = agent.predict()
    assert result.usage_stats is not None
    assert "ram_gb" in result.usage_stats
