import torch
from src.config import HEAR_MODEL_PATH
from src.utils.audio import load_audio, normalize_duration
from src.agent.safety import LowQualityError

class HeAREncoder:
    """
    Mock implementation of HeAR Encoder for initial setup.
    """
    def __init__(self):
        """Initialize the encoder."""
        print(f"Loading HeAR Encoder from {HEAR_MODEL_PATH}...")
        pass

    def encode(self, audio_path: str) -> torch.Tensor:
        """
        Extract embeddings from audio file using HeAR.
        
        Args:
            audio_path: Path to .wav file
            
        Returns:
            torch.Tensor: Embedding of shape (1, 1024)
            
        Raises:
            FileNotFoundError: If audio file not found
            LowQualityError: If audio is shorter than 1 second
        """
        # 1. Load audio and resample to 16kHz
        waveform, sr = load_audio(audio_path, sr=16000)
        
        # 2. Validate duration (FR2, AC1) - Must be at least 1 second
        if len(waveform) < sr:
            raise LowQualityError("Audio recording is too short (minimum 1 second required)")
            
        # 3. Normalize duration to 10 seconds (truncation/padding) (AC3)
        normalized_waveform = normalize_duration(waveform, target_length=10.0, sr=sr)
        
        # 4. Extract embedding (Mocked for now) (AC2)
        # In a real implementation, this would involve the model forward pass
        # print(f"Processing {len(normalized_waveform)} samples for embedding...")
        
        # Return mock tensor of shape (1, 1024) for now as established in Story 1.1
        return torch.randn(1, 1024)
