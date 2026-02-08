import unittest
import sys
import os
# Insert root and mocks path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'mocks')))

import torch
import numpy as np
from src.models.hear_encoder import HeAREncoder
from src.models.medgemma import MedGemmaReasoning
from src.models.data_types import PatientVitals, TriageResult, TriageStatus

class TestModels(unittest.TestCase):
    def setUp(self):
        self.hear = HeAREncoder()
        self.medgemma = MedGemmaReasoning()

    def test_hear_encoding(self):
        # Mocking audio components since implementation now requires them
        with unittest.mock.patch('src.models.hear_encoder.load_audio') as mock_load:
            with unittest.mock.patch('src.models.hear_encoder.normalize_duration') as mock_norm:
                # Setup mocks
                sr = 16000
                dummy_audio = np.zeros(sr * 5)
                mock_load.return_value = (dummy_audio, sr)
                mock_norm.return_value = np.zeros(sr * 10)
                
                embedding = self.hear.encode("dummy.wav")
                self.assertIsInstance(embedding, torch.Tensor)
                self.assertEqual(embedding.shape, (1, 1024))
                
                mock_load.assert_called_once()
                mock_norm.assert_called_once()

    def test_medgemma_generation(self):
        embedding = torch.randn(1, 1024)
        vitals = PatientVitals(age_months=12, respiratory_rate=30)
        result = self.medgemma.generate(embedding, vitals)
        
        self.assertIsInstance(result, TriageResult)
        self.assertIsInstance(result.status, TriageStatus)
        self.assertGreater(result.confidence, 0.0)
