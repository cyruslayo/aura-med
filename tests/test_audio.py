import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Insert root and mocks path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'mocks')))

# Mock librosa before importing audio utils
mock_librosa = MagicMock()
sys.modules['librosa'] = mock_librosa

from src.utils.audio import load_audio, normalize_duration

class TestAudioUtils(unittest.TestCase):
    def setUp(self):
        mock_librosa.reset_mock()

    def test_load_audio_success(self):
        # Setup mock
        audio_path = "test.wav"
        # We don't actually need the file to exist because we mock os.path.exists
        # in a real scenario we might need to mock os.path.exists or create a temp file
        # But here load_audio checks os.path.exists
        
        with unittest.mock.patch('os.path.exists', return_value=True):
            expected_sr = 16000
            dummy_audio = np.zeros(expected_sr * 5)
            mock_librosa.load.return_value = (dummy_audio, expected_sr)
            
            # Execute
            audio, sr = load_audio(audio_path, sr=expected_sr)
            
            # Verify
            self.assertEqual(sr, expected_sr)
            self.assertEqual(len(audio), expected_sr * 5)
            mock_librosa.load.assert_called_once_with(audio_path, sr=expected_sr, mono=True)

    def test_normalize_duration_truncation(self):
        sr = 16000
        audio = np.zeros(sr * 15) # 15 seconds
        target_length = 10.0
        
        normalized = normalize_duration(audio, target_length=target_length, sr=sr)
        
        self.assertEqual(len(normalized), sr * target_length)

    def test_normalize_duration_padding(self):
        sr = 16000
        audio = np.zeros(sr * 5) # 5 seconds
        target_length = 10.0
        
        normalized = normalize_duration(audio, target_length=target_length, sr=sr)
        
        self.assertEqual(len(normalized), sr * target_length)
        self.assertTrue(np.all(normalized[sr*5:] == 0))

    def test_load_audio_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_audio("non_existent.wav")

if __name__ == '__main__':
    unittest.main()
