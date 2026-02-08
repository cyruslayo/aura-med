import os
import librosa
import numpy as np

def load_audio(path, sr=16000):
    """
    Load an audio file and resample to the target sample rate.
    
    Args:
        path (str): Path to the audio file.
        sr (int): Target sample rate. Default is 16000.
        
    Returns:
        tuple: (waveform, sample_rate)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")
        
    # librosa.load resamples to sr and converts to mono by default
    waveform, sample_rate = librosa.load(path, sr=sr, mono=True)
    return waveform, sample_rate

def normalize_duration(audio, target_length=10.0, sr=16000):
    """
    Truncate or zero-pad audio to the target duration.
    
    Args:
        audio (np.ndarray): Input waveform.
        target_length (float): Target duration in seconds.
        sr (int): Sample rate.
        
    Returns:
        np.ndarray: Normalized waveform.
    """
    target_samples = int(target_length * sr)
    current_samples = len(audio)
    
    if current_samples > target_samples:
        # Truncate
        return audio[:target_samples]
    elif current_samples < target_samples:
        # Zero-pad
        padding = np.zeros(target_samples - current_samples)
        return np.concatenate((audio, padding))
    else:
        return audio
