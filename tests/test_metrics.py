"""Tests for metrics utility (R2)."""
import pytest
from src.datatypes import TriageStatus
from src.utils.metrics import compute_confusion_matrix, compute_metrics, render_metrics_html


class TestConfusionMatrix:
    def test_perfect_predictions(self):
        expected = [TriageStatus.GREEN, TriageStatus.YELLOW, TriageStatus.GREEN]
        predicted = [TriageStatus.GREEN, TriageStatus.YELLOW, TriageStatus.GREEN]
        
        matrix = compute_confusion_matrix(expected, predicted)
        assert matrix["GREEN"]["GREEN"] == 2
        assert matrix["YELLOW"]["YELLOW"] == 1
        assert matrix["GREEN"]["YELLOW"] == 0
    
    def test_misclassifications(self):
        expected = [TriageStatus.GREEN, TriageStatus.YELLOW]
        predicted = [TriageStatus.YELLOW, TriageStatus.GREEN]
        
        matrix = compute_confusion_matrix(expected, predicted)
        assert matrix["GREEN"]["YELLOW"] == 1  # FP
        assert matrix["YELLOW"]["GREEN"] == 1  # FN
        assert matrix["GREEN"]["GREEN"] == 0
        assert matrix["YELLOW"]["YELLOW"] == 0


class TestComputeMetrics:
    def test_perfect_sensitivity(self):
        expected = [TriageStatus.YELLOW, TriageStatus.YELLOW, TriageStatus.GREEN]
        predicted = [TriageStatus.YELLOW, TriageStatus.YELLOW, TriageStatus.GREEN]
        
        metrics = compute_metrics(expected, predicted)
        assert metrics["sensitivity"] == 1.0
        assert metrics["specificity"] == 1.0
        assert metrics["accuracy"] == 1.0
    
    def test_zero_sensitivity(self):
        """All YELLOW predicted as GREEN = 0% sensitivity."""
        expected = [TriageStatus.YELLOW, TriageStatus.YELLOW]
        predicted = [TriageStatus.GREEN, TriageStatus.GREEN]
        
        metrics = compute_metrics(expected, predicted)
        assert metrics["sensitivity"] == 0.0
    
    def test_mixed_results(self):
        expected = [
            TriageStatus.YELLOW, TriageStatus.YELLOW,
            TriageStatus.GREEN, TriageStatus.GREEN, TriageStatus.GREEN
        ]
        predicted = [
            TriageStatus.YELLOW, TriageStatus.GREEN,   # 1 TP, 1 FN
            TriageStatus.GREEN, TriageStatus.GREEN, TriageStatus.YELLOW  # 2 TN, 1 FP
        ]
        
        metrics = compute_metrics(expected, predicted)
        assert metrics["sensitivity"] == 0.5   # 1/2
        assert metrics["accuracy"] == 0.6      # 3/5
    
    def test_empty_inputs(self):
        metrics = compute_metrics([], [])
        assert metrics["accuracy"] == 0.0
        assert metrics["total_samples"] == 0


class TestRenderMetricsHTML:
    def test_renders_html_string(self):
        expected = [TriageStatus.GREEN, TriageStatus.YELLOW]
        predicted = [TriageStatus.GREEN, TriageStatus.YELLOW]
        metrics = compute_metrics(expected, predicted)
        
        html = render_metrics_html(metrics)
        assert "Validation Metrics" in html
        assert "Sensitivity" in html
        assert "Confusion Matrix" in html
    
    def test_pass_fail_indicators(self):
        """Should show ✅ when targets met."""
        expected = [TriageStatus.YELLOW] * 10 + [TriageStatus.GREEN] * 10
        predicted = expected.copy()  # Perfect
        metrics = compute_metrics(expected, predicted)
        
        html = render_metrics_html(metrics)
        assert "✅" in html
