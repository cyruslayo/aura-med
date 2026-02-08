import numpy as np

def load(path, sr=None, mono=True):
    # Mock loading: return 5 seconds of silence (16kHz)
    sample_rate = sr if sr is not None else 16000
    duration = 5
    waveform = np.zeros(sample_rate * duration)
    return waveform, sample_rate

def get_duration(y=None, sr=16000):
    if y is not None:
        return len(y) / sr
    return 0
