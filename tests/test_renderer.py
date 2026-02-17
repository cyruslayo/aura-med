import sys
from unittest.mock import MagicMock

# Mock IPython if not available
try:
    from IPython.display import HTML
except ImportError:
    class HTML:
        def __init__(self, data):
            self.data = data
    mock_display = MagicMock()
    mock_display.HTML = HTML
    sys.modules["IPython"] = MagicMock()
    sys.modules["IPython.display"] = mock_display

from src.datatypes import TriageResult, TriageStatus
from src.visualization.renderer import NotebookRenderer

def test_renderer_initialization():
    renderer = NotebookRenderer()
    assert renderer is not None

def test_render_green_status():
    renderer = NotebookRenderer()
    result = TriageResult(
        status=TriageStatus.GREEN,
        confidence=0.95,
        reasoning="Normal breath sounds detected.",
        action_recommendation="Soothe throat, return if symptoms worsen.",
        usage_stats={"ram_gb": 1.2, "latency_s": 4.5}
    )
    output = renderer.render(result)
    assert isinstance(output, HTML)
    assert "GREEN" in output.data
    assert "background-color: #2ECC71" in output.data
    assert "color: white" in output.data
    assert "max-width: 400px" in output.data
    assert "1.2 GB" in output.data

def test_render_yellow_status_readability():
    renderer = NotebookRenderer()
    result = TriageResult(
        status=TriageStatus.YELLOW,
        confidence=0.80,
        reasoning="Suspicious sounds.",
        usage_stats={"ram_gb": 2.0}
    )
    output = renderer.render(result)
    assert "YELLOW" in output.data
    assert "background-color: #F1C40F" in output.data
    assert "color: #2c3e50" in output.data  # Readability fix check

def test_render_red_status():
    renderer = NotebookRenderer()
    result = TriageResult(
        status=TriageStatus.RED,
        confidence=0.98,
        reasoning="Severe distress.",
        action_recommendation="IMMEDIATE REFERRAL"
    )
    output = renderer.render(result)
    assert "RED" in output.data
    assert "background-color: #E74C3C" in output.data
    assert "IMMEDIATE REFERRAL" in output.data

def test_render_xss_protection():
    renderer = NotebookRenderer()
    result = TriageResult(
        status=TriageStatus.GREEN,
        confidence=1.0,
        reasoning="<script>alert('XSS')</script>",
        action_recommendation="<b>Strong</b>"
    )
    output = renderer.render(result)
    # Check that tags are escaped
    assert "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;" in output.data
    assert "&lt;b&gt;Strong&lt;/b&gt;" in output.data
    assert "<script>" not in output.data

def test_render_no_telemetry():
    renderer = NotebookRenderer()
    result = TriageResult(
        status=TriageStatus.GREEN,
        confidence=0.5,
        reasoning="Unknown"
    )
    output = renderer.render(result)
    assert "EDGE SIM: N/A RAM" in output.data
