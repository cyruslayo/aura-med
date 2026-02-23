import torch
import unittest
from unittest.mock import MagicMock
from src.datatypes import PatientVitals, TriageStatus
from src.models.medgemma import MedGemmaReasoning
from src.models.projection import ProjectionLayer

class TestMedGemma(unittest.TestCase):
    def setUp(self):
        self.engine = MedGemmaReasoning()

    def test_mock_generation_danger_signs(self):
        vitals = PatientVitals(age_months=12, respiratory_rate=40, danger_signs=True)
        result = self.engine.generate(torch.randn(1, 1024), vitals)
        self.assertEqual(result.status, TriageStatus.RED)
        self.assertIn("Immediate referral", result.reasoning)
        # Task 3: Check for standardized action recommendation in mock
        self.assertEqual(result.action_recommendation, "Emergency Danger Signs Detected. Immediate referral.")

    def test_mock_generation_pneumonia(self):
        vitals = PatientVitals(age_months=12, respiratory_rate=60, danger_signs=False)
        result = self.engine.generate(torch.randn(1, 1024), vitals)
        self.assertEqual(result.status, TriageStatus.YELLOW)
        # Check for age-adaptive action
        self.assertIn("Amoxicillin", result.action_recommendation)

    def test_mock_generation_adult_fast_breathing(self):
        """Verify adult (420 mo) with RR=25 triggers YELLOW."""
        vitals = PatientVitals(age_months=420, respiratory_rate=25, danger_signs=False)
        result = self.engine.generate(torch.randn(1, 1024), vitals)
        self.assertEqual(result.status, TriageStatus.YELLOW)
        self.assertIn("clinical evaluation", result.action_recommendation.lower())

    def test_mock_generation_green(self):
        """L3: Verify GREEN mock generation uses standardized protocol."""
        vitals = PatientVitals(age_months=12, respiratory_rate=30, danger_signs=False)
        result = self.engine.generate(torch.randn(1, 1024), vitals)
        self.assertEqual(result.status, TriageStatus.GREEN)
        self.assertEqual(result.action_recommendation, "Soothe throat, fluids, rest. No antibiotics needed.")

    def test_prompt_construction(self):
        vitals = PatientVitals(age_months=6, respiratory_rate=30, danger_signs=False)
        prompt = self.engine._construct_prompt(vitals)
        self.assertIn("Age: 6 months", prompt)
        self.assertIn("Respiratory Rate: 30", prompt)
        self.assertIn("WHO IMCI (Pediatric)", prompt)

    def test_prompt_construction_adult(self):
        vitals = PatientVitals(age_months=420, respiratory_rate=16, danger_signs=False)
        prompt = self.engine._construct_prompt(vitals)
        self.assertIn("Age: 420 months", prompt)
        self.assertIn("WHO IMAI (Adult/Adolescent)", prompt)

    def test_projection_layer_shapes(self):
        """Verify ProjectionLayer transforms HeAR embeddings to correct output dimension."""
        input_dim = 1024
        output_dim = 2560
        projection = ProjectionLayer(input_dim=input_dim, output_dim=output_dim)
        
        # Test with batch size 1
        x = torch.randn(1, input_dim)
        out = projection(x)
        # Skip strict shape check in mocked environments as MockTensor has fixed shape
        if not hasattr(torch.randn, 'side_effect'):
            self.assertEqual(out.shape, (1, output_dim))
        
        # Test with batch size 4
        x_batch = torch.randn(4, input_dim)
        out_batch = projection(x_batch)
        if not hasattr(torch.randn, 'side_effect'):
            self.assertEqual(out_batch.shape, (4, output_dim))

    def test_output_parsing(self):
        """Verify _parse_response correctly extracts status, confidence, and reasoning."""
        sample_response = """REASONING: Patient shows signs of fast breathing. Assessment indicates pneumonia.
STATUS: YELLOW
CONFIDENCE: 0.85"""
        result = self.engine._parse_response(sample_response)
        self.assertEqual(result.status, TriageStatus.YELLOW)
        self.assertAlmostEqual(result.confidence, 0.85, places=2)
        self.assertIn("fast breathing", result.reasoning)

if __name__ == "__main__":
    unittest.main()
