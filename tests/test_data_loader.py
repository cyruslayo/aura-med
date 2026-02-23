"""Tests for ICBHIDataset validation mode (R1)."""
import pytest
from unittest.mock import patch, MagicMock
from src.data.icbhi_loader import ICBHIDataset


class TestICBHIValidationMode:
    """Tests for the mode parameter in get_samples()."""
    
    @pytest.fixture
    def mock_dataset(self, tmp_path):
        """Create a mock dataset with known samples."""
        # Create fake audio files
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        
        diagnoses = {
            101: "Pneumonia",
            102: "Healthy",
            103: "Bronchiolitis",
        }
        
        for pid in diagnoses:
            for i in range(3):
                (audio_dir / f"{pid}_{i}_Tc_sc.wav").touch()
        
        # Create diagnosis file
        diag_file = tmp_path / "ICBHI_diagnosis.txt"
        diag_file.write_text("\n".join(f"{pid}\t{diag}" for pid, diag in diagnoses.items()))
        
        with patch.object(ICBHIDataset, '__init__', lambda self: None):
            dataset = ICBHIDataset()
            dataset.data_dir = str(tmp_path)
            dataset.patient_diagnoses = diagnoses
            dataset.patient_ages = {101: 1, 102: 3, 103: 2}
            
            # Populate samples_by_diagnosis
            dataset.samples_by_diagnosis = {}
            for pid, diag in diagnoses.items():
                if diag not in dataset.samples_by_diagnosis:
                    dataset.samples_by_diagnosis[diag] = []
                for i in range(3):
                    dataset.samples_by_diagnosis[diag].append(
                        str(audio_dir / f"{pid}_{i}_Tc_sc.wav")
                    )
        
        return dataset
    
    def test_validation_mode_uses_neutral_rr(self, mock_dataset):
        """In validation mode, ALL samples should have RR=35 regardless of diagnosis."""
        samples = mock_dataset.get_samples(n=9, mode="validation", shuffle=False)
        
        for sample in samples:
            assert sample.vitals.respiratory_rate == 35, (
                f"Validation mode should use neutral RR=35, got {sample.vitals.respiratory_rate} "
                f"for diagnosis={sample.diagnosis}"
            )
    
    def test_demo_mode_uses_diagnosis_aligned_rr(self, mock_dataset):
        """In demo mode, sick patients should have fast RR, healthy should have normal."""
        samples = mock_dataset.get_samples(n=9, mode="demo", shuffle=False)
        
        for sample in samples:
            if sample.diagnosis == "Pneumonia":
                assert sample.vitals.respiratory_rate == 55
            elif sample.diagnosis == "Healthy":
                assert sample.vitals.respiratory_rate == 28
    
    def test_default_mode_is_demo(self, mock_dataset):
        """Default mode should be 'demo' for backward compatibility."""
        samples = mock_dataset.get_samples(n=3, shuffle=False)
        # At least one pneumonia sample should have RR=55
        pneumonia_samples = [s for s in samples if s.diagnosis == "Pneumonia"]
        if pneumonia_samples:
            assert pneumonia_samples[0].vitals.respiratory_rate == 55
    
    def test_invalid_mode_raises(self, mock_dataset):
        """Invalid mode should raise ValueError."""
        with pytest.raises(ValueError, match="mode must be"):
            mock_dataset.get_samples(n=3, mode="invalid")
    
    def test_get_validation_samples_convenience(self, mock_dataset):
        """get_validation_samples() should use validation mode."""
        samples = mock_dataset.get_validation_samples(n=9, shuffle=False)
        
        for sample in samples:
            assert sample.vitals.respiratory_rate == 35
