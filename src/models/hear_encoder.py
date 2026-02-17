import logging
import torch
import numpy as np
from typing import Union
from src.config import (
    HEAR_EMBEDDING_DIM,
    HEAR_CHUNK_DURATION_SEC,
    NOISE_RMS_UPPER_THRESHOLD, 
    NOISE_RMS_LOWER_THRESHOLD,
    MIN_AUDIO_DURATION_SEC,
    SAMPLE_RATE,
    IS_DEMO_MODE
)
from src.utils.audio import load_audio, normalize_duration
from src.datatypes import LowQualityError

logger = logging.getLogger(__name__)

# HuggingFace model ID for HeAR (official Google release)
HEAR_HF_MODEL_ID = "google/hear"


class HeAREncoder:
    """
    HeAR (Health Acoustic Representations) Encoder.
    
    Extracts 512-dimensional embeddings from audio using Google's HeAR model
    loaded from HuggingFace via from_pretrained_keras.
    Falls back to deterministic mock embeddings when model is unavailable.
    """
    
    def __init__(self):
        """Initialize the HeAR encoder, loading the real model if available."""
        self.model = None
        self.embedding_dim = HEAR_EMBEDDING_DIM
        
        if not IS_DEMO_MODE:
            self._load_model()
        else:
            logger.info("HeAR Encoder initialized in DEMO mode (no GPU). Using mock embeddings.")
            print("⚠️ HeAR in DEMO mode (no GPU). Using mock embeddings.")
    
    def _load_model(self):
        """
        Load the real HeAR model from HuggingFace Hub.
        
        Downloads the SavedModel via snapshot_download, then loads it
        with tf.saved_model.load. Compatible with all huggingface_hub versions.
        """
        try:
            import tensorflow as tf
            from huggingface_hub import snapshot_download
            
            logger.info("Loading HeAR Encoder from HuggingFace: %s", HEAR_HF_MODEL_ID)
            print(f"🔄 Downloading HeAR model from HuggingFace ({HEAR_HF_MODEL_ID})...")
            
            # Download the full model repository
            model_dir = snapshot_download(HEAR_HF_MODEL_ID)
            
            print(f"🔄 Loading HeAR SavedModel...")
            self.model = tf.saved_model.load(model_dir)
            
            logger.info("HeAR Encoder loaded successfully from %s", model_dir)
            print("✅ HeAR Encoder loaded successfully.")
        except ImportError as e:
            logger.error("Missing dependency for HeAR: %s", str(e))
            print(f"⚠️ Missing dependency: {e}. Using mock embeddings.")
        except Exception as e:
            logger.error("Failed to load HeAR model: %s", str(e))
            print(f"⚠️ HeAR model load failed: {e}. Using mock embeddings.")

    def _detect_noise(self, waveform: Union[torch.Tensor, np.ndarray]) -> float:
        """
        Estimate noise level in the waveform using RMS.
        
        Args:
            waveform: Audio waveform as a torch tensor or numpy array.
            
        Returns:
            float: Root Mean Square (RMS) value of the waveform.
        """
        if isinstance(waveform, torch.Tensor):
            wf_np = waveform.numpy()
        else:
            wf_np = waveform
            
        rms = np.sqrt(np.mean(wf_np**2))
        return float(rms)

    def _segment_audio(self, waveform: np.ndarray, sr: int) -> np.ndarray:
        """
        Segment audio into fixed-length chunks for HeAR processing.
        
        HeAR expects 2-second segments at 16kHz (32000 samples per chunk).
        Short final chunks are zero-padded to maintain consistent dimensions.
        
        Args:
            waveform: Audio waveform as numpy array.
            sr: Sample rate.
            
        Returns:
            np.ndarray: Array of shape (N, chunk_samples) containing audio chunks.
        """
        chunk_samples = int(sr * HEAR_CHUNK_DURATION_SEC)
        chunks = []
        
        for i in range(0, len(waveform), chunk_samples):
            chunk = waveform[i:i + chunk_samples]
            if len(chunk) < chunk_samples:
                # Zero-pad short final chunk
                chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), mode='constant')
            chunks.append(chunk)
        
        return np.array(chunks, dtype=np.float32)

    def encode(self, audio_path: str) -> torch.Tensor:
        """
        Extract embeddings from audio file using HeAR.
        
        Pipeline: Load → Validate → Segment → Encode → Average → Return
        
        Args:
            audio_path: Path to .wav file
            
        Returns:
            torch.Tensor: Embedding of shape (1, 512)
            
        Raises:
            FileNotFoundError: If audio file not found
            LowQualityError: If audio is shorter than threshold or too noisy/silent
        """
        # 1. Load audio and resample to 16kHz
        waveform, sr = load_audio(audio_path, sr=SAMPLE_RATE)
        
        # 2. Validate duration
        if len(waveform) < sr * MIN_AUDIO_DURATION_SEC:
            raise LowQualityError(
                f"Audio recording is too short (minimum {MIN_AUDIO_DURATION_SEC} second required)"
            )
            
        # 3. Validate noise level
        noise_level = self._detect_noise(waveform)
        if noise_level > NOISE_RMS_UPPER_THRESHOLD:
            raise LowQualityError("Audio recording is too noisy or distorted")
        if noise_level < NOISE_RMS_LOWER_THRESHOLD:
            raise LowQualityError("Audio recording contains no clear signal (too silent)")

        # 4. Normalize duration to max seconds (truncation/padding)
        normalized_waveform = normalize_duration(waveform, target_length=10.0, sr=sr)
        
        # 5. Extract embedding
        if self.model is not None:
            return self._encode_real(normalized_waveform, sr)
        else:
            return self._encode_mock()
    
    def _encode_real(self, waveform: np.ndarray, sr: int) -> torch.Tensor:
        """
        Extract real embeddings using the loaded HeAR model.
        
        Segments audio into 2-second chunks, extracts per-chunk embeddings
        via the model's serving signature, and returns the mean embedding.
        
        Based on Google's official HeAR example notebook:
          infer = model.signatures["serving_default"]
          output = infer(x=tf.constant(chunk, dtype=tf.float32))
          embedding = output['output_0']
        """
        import tensorflow as tf
        
        # Segment into 2-second chunks
        chunks = self._segment_audio(waveform, sr)
        logger.info("Processing %d audio chunks through HeAR", len(chunks))
        
        # Get the serving inference function
        infer = self.model.signatures["serving_default"]
        
        # Extract embeddings for each chunk
        all_embeddings = []
        for chunk in chunks:
            # HeAR expects shape (1, 32000) — one 2-second clip at 16kHz
            input_tensor = np.expand_dims(chunk, axis=0)
            output = infer(x=tf.constant(input_tensor, dtype=tf.float32))
            embedding = output['output_0'].numpy()  # shape (1, 512)
            all_embeddings.append(embedding)
        
        # Stack and average across chunks
        stacked = np.concatenate(all_embeddings, axis=0)  # (N, 512)
        avg_embedding = np.mean(stacked, axis=0, keepdims=True)  # (1, 512)
        
        # Convert to PyTorch tensor
        result = torch.from_numpy(avg_embedding).float()
        logger.info("HeAR embedding shape: %s", result.shape)
        
        return result
    
    def _encode_mock(self) -> torch.Tensor:
        """
        Return mock embeddings for demo/testing (no GPU available).
        Uses deterministic random for reproducibility.
        """
        logger.info("Using mock HeAR embedding (no model loaded)")
        # Use torch.randn for compatibility with test mock framework
        torch.manual_seed(42)
        return torch.randn(1, self.embedding_dim)
