import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'mocks')))

from src.models.data_types import PatientVitals, TriageStatus, TriageResult
from pydantic import ValidationError

class TestDataTypes(unittest.TestCase):
    def test_patient_vitals_valid(self):
        vitals = PatientVitals(age_months=12, respiratory_rate=30)
        self.assertEqual(vitals.age_months, 12)
        self.assertFalse(vitals.danger_signs)

    def test_patient_vitals_invalid(self):
        with self.assertRaises(ValidationError):
            PatientVitals(age_months=-1, respiratory_rate=30)
