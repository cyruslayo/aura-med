"""
Metrics utilities for AuraMed validation.

Computes confusion matrix, sensitivity, specificity, F1 score,
and renders them as styled HTML for notebook display.
"""

from typing import List, Dict, Any
from collections import Counter
from src.datatypes import TriageStatus


def compute_confusion_matrix(
    expected: List[TriageStatus],
    predicted: List[TriageStatus]
) -> Dict[str, Dict[str, int]]:
    """
    Compute a confusion matrix for triage predictions.
    
    Returns a nested dict: matrix[actual][predicted] = count
    Labels are the TriageStatus values (GREEN, YELLOW, RED, INCONCLUSIVE).
    """
    labels = [TriageStatus.GREEN, TriageStatus.YELLOW, TriageStatus.RED, TriageStatus.INCONCLUSIVE]
    matrix = {act.value: {pred.value: 0 for pred in labels} for act in labels}
    
    for exp, pred in zip(expected, predicted):
        matrix[exp.value][pred.value] += 1
    
    return matrix


def compute_metrics(
    expected: List[TriageStatus],
    predicted: List[TriageStatus]
) -> Dict[str, Any]:
    """
    Compute clinical validation metrics.
    
    Returns dict with:
      - sensitivity: recall for YELLOW class (detect sick patients)
      - specificity: recall for GREEN class (correctly clear healthy)
      - accuracy: overall correct / total
      - f1_weighted: weighted F1 across all classes
      - per_class: dict of per-class precision/recall
    """
    matrix = compute_confusion_matrix(expected, predicted)
    total = len(expected)
    correct = sum(1 for e, p in zip(expected, predicted) if e == p)
    accuracy = correct / total if total > 0 else 0.0
    
    # Sensitivity = TP_yellow / (TP_yellow + FN_yellow)
    yellow = TriageStatus.YELLOW.value
    tp_yellow = matrix[yellow][yellow]
    fn_yellow = sum(matrix[yellow][p] for p in matrix[yellow]) - tp_yellow
    sensitivity = tp_yellow / (tp_yellow + fn_yellow) if (tp_yellow + fn_yellow) > 0 else 0.0
    
    # Specificity = TN_yellow / (TN_yellow + FP_yellow)
    # TN = all non-yellow correctly classified as non-yellow
    # FP = all non-yellow incorrectly classified as yellow
    fp_yellow = sum(matrix[a][yellow] for a in matrix if a != yellow)
    tn_yellow = sum(
        matrix[a][p] for a in matrix for p in matrix[a]
        if a != yellow and p != yellow
    )
    specificity = tn_yellow / (tn_yellow + fp_yellow) if (tn_yellow + fp_yellow) > 0 else 0.0
    
    # Weighted F1
    labels = [s.value for s in TriageStatus]
    f1_sum = 0.0
    weight_sum = 0
    per_class = {}
    
    for label in labels:
        tp = matrix[label][label]
        fp = sum(matrix[a][label] for a in matrix if a != label)
        fn = sum(matrix[label][p] for p in matrix[label] if p != label)
        support = tp + fn
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
        f1_sum += f1 * support
        weight_sum += support
    
    f1_weighted = f1_sum / weight_sum if weight_sum > 0 else 0.0
    
    return {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "accuracy": accuracy,
        "f1_weighted": f1_weighted,
        "total_samples": total,
        "correct": correct,
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def render_metrics_html(metrics: Dict[str, Any]) -> str:
    """Render metrics as styled HTML for notebook display."""
    
    # PRD targets
    sens_pass = "✅" if metrics["sensitivity"] >= 0.85 else "❌"
    spec_pass = "✅" if metrics["specificity"] >= 0.70 else "❌"
    
    matrix = metrics["confusion_matrix"]
    labels = ["GREEN", "YELLOW", "RED", "INCONCLUSIVE"]
    # Filter to only labels that have data
    active_labels = [l for l in labels if any(matrix[l][p] > 0 for p in labels) or any(matrix[a][l] > 0 for a in labels)]
    
    # Build confusion matrix HTML
    cm_rows = ""
    for act in active_labels:
        cells = ""
        for pred in active_labels:
            val = matrix[act][pred]
            bg = "#2ecc71" if act == pred and val > 0 else ("#fee" if val > 0 else "#fff")
            cells += f'<td style="text-align:center;padding:8px;background:{bg};font-weight:{"700" if act==pred else "400"}">{val}</td>'
        cm_rows += f'<tr><td style="padding:8px;font-weight:700;background:#f8f9fa">{act}</td>{cells}</tr>'
    
    cm_header = "".join(f'<th style="padding:8px;background:#ecf0f1">{l}</th>' for l in active_labels)
    
    return f"""
    <div style="font-family:'Inter',sans-serif;max-width:600px;margin:20px auto">
        <h3 style="text-align:center;color:#2c3e50">📊 Validation Metrics</h3>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
            <tr style="background:#f8f9fa">
                <th style="padding:10px;text-align:left">Metric</th>
                <th style="padding:10px;text-align:center">Value</th>
                <th style="padding:10px;text-align:center">Target</th>
                <th style="padding:10px;text-align:center">Status</th>
            </tr>
            <tr>
                <td style="padding:10px">Sensitivity (YELLOW recall)</td>
                <td style="padding:10px;text-align:center;font-weight:700">{metrics['sensitivity']:.1%}</td>
                <td style="padding:10px;text-align:center">≥85%</td>
                <td style="padding:10px;text-align:center">{sens_pass}</td>
            </tr>
            <tr style="background:#f8f9fa">
                <td style="padding:10px">Specificity (non-YELLOW recall)</td>
                <td style="padding:10px;text-align:center;font-weight:700">{metrics['specificity']:.1%}</td>
                <td style="padding:10px;text-align:center">≥70%</td>
                <td style="padding:10px;text-align:center">{spec_pass}</td>
            </tr>
            <tr>
                <td style="padding:10px">Accuracy</td>
                <td style="padding:10px;text-align:center;font-weight:700">{metrics['accuracy']:.1%}</td>
                <td style="padding:10px;text-align:center">—</td>
                <td style="padding:10px;text-align:center">—</td>
            </tr>
            <tr style="background:#f8f9fa">
                <td style="padding:10px">F1 (weighted)</td>
                <td style="padding:10px;text-align:center;font-weight:700">{metrics['f1_weighted']:.3f}</td>
                <td style="padding:10px;text-align:center">—</td>
                <td style="padding:10px;text-align:center">—</td>
            </tr>
        </table>
        
        <h4 style="text-align:center;color:#2c3e50">Confusion Matrix</h4>
        <table style="width:100%;border-collapse:collapse;border:1px solid #ddd">
            <tr>
                <th style="padding:8px;background:#2c3e50;color:white">Actual ↓ / Predicted →</th>
                {cm_header}
            </tr>
            {cm_rows}
        </table>
        <p style="font-size:11px;color:#95a5a6;text-align:center;margin-top:8px">
            n={metrics['total_samples']} | {metrics['correct']}/{metrics['total_samples']} correct
        </p>
    </div>
    """
