"""
ICBHI 2017 Respiratory Sound Database Loader.

Parses the ICBHI dataset metadata, maps medical diagnoses to AuraMed
TriageStatus values, and provides an iterator for batch validation.

Dataset structure expected:
    icbhi/
    ├── audio_and_txt_files/     # .wav + .txt annotation files
    ├── patient_diagnosis.csv    # patient_id,diagnosis
    └── demographic_info.txt     # patient_id,age,sex,...
"""

import os
import csv
import random
import logging
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from src.datatypes import PatientVitals, TriageStatus

logger = logging.getLogger(__name__)

# ── Diagnosis → Triage Mapping ──────────────────────────────────────────
# Based on WHO IMCI severity classification for respiratory illness
DIAGNOSIS_TO_TRIAGE: Dict[str, TriageStatus] = {
    "Pneumonia":        TriageStatus.YELLOW,
    "LRTI":             TriageStatus.YELLOW,
    "Bronchiolitis":    TriageStatus.YELLOW,
    "Bronchiectasis":   TriageStatus.YELLOW,
    "COPD":             TriageStatus.YELLOW,
    "Asthma":           TriageStatus.YELLOW,
    "URTI":             TriageStatus.GREEN,
    "Healthy":          TriageStatus.GREEN,
}

# Default vitals when age metadata is unavailable
DEFAULT_VITALS_SICK = PatientVitals(age_months=540, respiratory_rate=28, danger_signs=False)   # Adult default
DEFAULT_VITALS_HEALTHY = PatientVitals(age_months=540, respiratory_rate=16, danger_signs=False) # Adult default


@dataclass
class ICBHISample:
    """A single sample from the ICBHI dataset."""
    audio_path: str
    patient_id: int
    diagnosis: str
    expected_triage: TriageStatus
    vitals: PatientVitals


class ICBHIDataset:
    """
    Loader for the ICBHI 2017 Respiratory Sound Database.
    
    Usage:
        dataset = ICBHIDataset("/content/drive/MyDrive/aura-med/data/icbhi")
        samples = dataset.get_samples(n=5, diagnosis="Pneumonia")
        for sample in samples:
            result = agent.predict(sample.audio_path, sample.vitals)
            print(f"Expected: {sample.expected_triage}, Got: {result.status}")
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize the ICBHI dataset loader.
        
        Args:
            data_dir: Path to the ICBHI dataset root directory.
                      Will auto-discover 'patient_diagnosis.csv' and
                      'audio_and_txt_files/' even if nested in subdirectories
                      (common with Kaggle downloads).
        """
        self.data_dir = data_dir
        
        # Auto-discover the actual file locations
        self.diagnosis_file, self.audio_dir, self.demographic_file = \
            self._discover_paths(data_dir)
        
        # patient_id -> diagnosis string
        self.patient_diagnoses: Dict[int, str] = {}
        # patient_id -> age (if available)
        self.patient_ages: Dict[int, Optional[int]] = {}
        # All available audio files grouped by diagnosis
        self.samples_by_diagnosis: Dict[str, List[str]] = {}
        
        self._load_metadata()
    
    @staticmethod
    def _discover_paths(data_dir: str):
        """
        Walk the directory tree to find the key ICBHI files.
        
        The Kaggle download often nests files like:
          icbhi/Respiratory_Sound_Database/Respiratory_Sound_Database/
            ├── audio_and_txt_files/
            ├── patient_diagnosis.csv
            └── demographic_info.txt
        
        This method finds them regardless of nesting depth.
        """
        diagnosis_file = None
        audio_dir = None
        demographic_file = None
        
        for root, dirs, files in os.walk(data_dir):
            for f in files:
                if f == "patient_diagnosis.csv" and diagnosis_file is None:
                    diagnosis_file = os.path.join(root, f)
                if f == "demographic_info.txt" and demographic_file is None:
                    demographic_file = os.path.join(root, f)
            for d in dirs:
                if d == "audio_and_txt_files" and audio_dir is None:
                    audio_dir = os.path.join(root, d)
        
        if diagnosis_file is None:
            raise FileNotFoundError(
                f"Could not find 'patient_diagnosis.csv' anywhere under: {data_dir}\n"
                f"Please ensure the ICBHI dataset is fully extracted there."
            )
        if audio_dir is None:
            raise FileNotFoundError(
                f"Could not find 'audio_and_txt_files/' directory under: {data_dir}\n"
                f"Please ensure the ICBHI dataset is fully extracted there."
            )
        
        logger.info("Discovered ICBHI paths:\n  diagnosis: %s\n  audio: %s",
                     diagnosis_file, audio_dir)
        print(f"📂 Found diagnosis file: {diagnosis_file}")
        print(f"📂 Found audio directory: {audio_dir}")
        
        return diagnosis_file, audio_dir, demographic_file
    
    def _load_metadata(self):
        """Load patient diagnoses and map audio files."""
        # 1. Parse patient_diagnosis.csv
        if not os.path.exists(self.diagnosis_file):
            raise FileNotFoundError(
                f"ICBHI diagnosis file not found: {self.diagnosis_file}\n"
                f"Please ensure the dataset is extracted to: {self.data_dir}"
            )
        
        with open(self.diagnosis_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    try:
                        pid = int(parts[0].strip())
                        diag = parts[1].strip()
                        self.patient_diagnoses[pid] = diag
                    except ValueError:
                        continue
        
        logger.info("Loaded %d patient diagnoses", len(self.patient_diagnoses))
        
        # 2. Parse demographic_info.txt for ages (optional)
        if os.path.exists(self.demographic_file):
            with open(self.demographic_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[0])
                            age = int(parts[1])
                            self.patient_ages[pid] = age
                        except ValueError:
                            continue
        
        # 3. Index audio files by diagnosis
        if not os.path.exists(self.audio_dir):
            raise FileNotFoundError(
                f"ICBHI audio directory not found: {self.audio_dir}\n"
                f"Expected structure: {self.data_dir}/audio_and_txt_files/*.wav"
            )
        
        for fname in os.listdir(self.audio_dir):
            if not fname.endswith(".wav"):
                continue
            # ICBHI filenames: {patient_id}_{recording}_{chest_loc}_{acq_mode}_{rec_equip}.wav
            try:
                pid = int(fname.split("_")[0])
            except (ValueError, IndexError):
                continue
            
            diag = self.patient_diagnoses.get(pid)
            if diag is None:
                continue
            
            if diag not in self.samples_by_diagnosis:
                self.samples_by_diagnosis[diag] = []
            self.samples_by_diagnosis[diag].append(os.path.join(self.audio_dir, fname))
        
        total = sum(len(v) for v in self.samples_by_diagnosis.values())
        logger.info("Indexed %d audio files across %d diagnoses", total, len(self.samples_by_diagnosis))
    
    def get_diagnosis_counts(self) -> Dict[str, int]:
        """Return a dict of diagnosis -> number of audio files."""
        return {k: len(v) for k, v in sorted(self.samples_by_diagnosis.items())}
    
    def get_samples(
        self, 
        n: int = 5, 
        diagnosis: Optional[str] = None,
        shuffle: bool = True,
        mode: str = "demo"
    ) -> List[ICBHISample]:
        """
        Get N samples from the dataset, optionally filtered by diagnosis.
        
        Args:
            n: Number of samples to return.
            diagnosis: Filter to a specific diagnosis (e.g. "Pneumonia").
                       If None, samples from all diagnoses.
            shuffle: Whether to randomly shuffle before selecting.
            mode: "demo" uses diagnosis-aligned vitals for demo journeys.
                  "validation" uses neutral vitals (RR=35) so the model
                  must rely on HeAR audio features, not baked-in vitals.
            
        Returns:
            List of ICBHISample objects with audio path, expected triage, and vitals.
        """
        if mode not in ("demo", "validation"):
            raise ValueError(f"mode must be 'demo' or 'validation', got '{mode}'")

        if diagnosis:
            pool = self.samples_by_diagnosis.get(diagnosis, [])
            if not pool:
                available = list(self.samples_by_diagnosis.keys())
                raise ValueError(
                    f"No samples for diagnosis '{diagnosis}'. "
                    f"Available: {available}"
                )
        else:
            pool = []
            for files in self.samples_by_diagnosis.values():
                pool.extend(files)
        
        if shuffle:
            pool = list(pool)
            random.shuffle(pool)
        
        selected = pool[:n]
        samples = []
        for audio_path in selected:
            fname = os.path.basename(audio_path)
            try:
                pid = int(fname.split("_")[0])
            except (ValueError, IndexError):
                continue
            
            diag = self.patient_diagnoses.get(pid, "Unknown")
            expected = DIAGNOSIS_TO_TRIAGE.get(diag, TriageStatus.INCONCLUSIVE)
            
            # Build vitals based on available metadata
            age_years = self.patient_ages.get(pid)
            if age_years is not None:
                age_months = age_years * 12
            else:
                age_months = 18  # Default
            
            if mode == "validation":
                # Neutral vitals — model must rely on acoustic features
                # Use a rate that is "Normal" for whatever age the patient is
                from src.datatypes import get_fast_breathing_threshold
                threshold = get_fast_breathing_threshold(age_months)
                
                vitals = PatientVitals(
                    age_months=age_months,
                    respiratory_rate=threshold - 5,  # Consistently below threshold
                    danger_signs=False
                )
            else:
                # Demo mode — diagnosis-aligned vitals for predictable output
                from src.datatypes import get_fast_breathing_threshold
                threshold = get_fast_breathing_threshold(age_months)
                
                if expected == TriageStatus.YELLOW:
                    vitals = PatientVitals(
                        age_months=age_months,
                        respiratory_rate=threshold + 10,  # Fast breathing for age
                        danger_signs=False
                    )
                else:
                    vitals = PatientVitals(
                        age_months=age_months,
                        respiratory_rate=threshold - 8,  # Normal
                        danger_signs=False
                    )
            
            samples.append(ICBHISample(
                audio_path=audio_path,
                patient_id=pid,
                diagnosis=diag,
                expected_triage=expected,
                vitals=vitals
            ))
        
        return samples

    def get_validation_samples(
        self,
        n: int = 10,
        diagnosis: Optional[str] = None,
        shuffle: bool = True
    ) -> List[ICBHISample]:
        """Convenience method: get samples with neutral vitals for unbiased validation."""
        return self.get_samples(n=n, diagnosis=diagnosis, shuffle=shuffle, mode="validation")
    
    def summary(self) -> str:
        """Return a human-readable summary of the loaded dataset."""
        lines = [f"ICBHI Dataset: {self.data_dir}"]
        lines.append(f"Patients: {len(self.patient_diagnoses)}")
        total = sum(len(v) for v in self.samples_by_diagnosis.values())
        lines.append(f"Audio Files: {total}")
        lines.append("")
        lines.append("Diagnosis Distribution:")
        for diag, files in sorted(self.samples_by_diagnosis.items(), key=lambda x: -len(x[1])):
            triage = DIAGNOSIS_TO_TRIAGE.get(diag, TriageStatus.INCONCLUSIVE)
            lines.append(f"  {diag:20s} → {triage.value:12s} ({len(files)} files)")
        return "\n".join(lines)
