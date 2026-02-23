import sys
from unittest.mock import MagicMock

# Global Mocks for Heavy Dependencies
def setup_global_mocks():
    mock_modules = ["transformers", "bitsandbytes", "torch", "torch.nn", "torch.nn.functional", "librosa", "accelerate"]
    for module_name in mock_modules:
        if module_name not in sys.modules:
            m = MagicMock()
            sys.modules[module_name] = m
        else:
            m = sys.modules[module_name]
            
        if module_name == "torch":
            m.nn = MagicMock()
            # Mock nn.Module as a real class so super().__init__ works
            class MockModule:
                def __init__(self, *args, **kwargs): pass
                def __call__(self, *args, **kwargs): 
                    # Return a MockTensor that can handle shape checks
                    return MockTensor((1, 512))
                def to(self, *args, **kwargs): return self
                def cuda(self, *args, **kwargs): return self
                def parameters(self): return []
                def eval(self): return self
                def train(self, mode=True): return self
            m.nn.Module = MockModule
            
            class MockTensor:
                def __init__(self, *args, **kwargs):
                    if args and isinstance(args[0], (list, tuple)):
                        self.shape = tuple(args[0])
                    else:
                        self.shape = args
                def __getitem__(self, idx): return self
                def __len__(self): return self.shape[0] if self.shape else 0
                def to(self, *args, **kwargs): return self
                def size(self): return self.shape
                def float(self): return self
                def squeeze(self): return self
                def detach(self): return self
                def cpu(self): return self
                def numpy(self):
                    import numpy as np
                    dim = self.shape[-1] if self.shape else 512
                    return np.random.randn(dim).astype(np.float32)
            
            def mock_randn(*args, **kwargs):
                return MockTensor(*args)
            
            m.Tensor = MockTensor
            m.randn.side_effect = mock_randn
            m.cuda.is_available.return_value = False
            m.float32 = "float32"
            m.float16 = "float16"
            
            # Mock torch.no_grad as a context manager
            class MockNoGrad:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            m.no_grad = MockNoGrad
        elif module_name == "torch.nn":
            class MockModule:
                def __init__(self, *args, **kwargs): pass
                def __call__(self, *args, **kwargs): return MockTensor((1, 512))
                def eval(self): return self
                def train(self, mode=True): return self
            m.Module = MockModule
            m.Linear = MagicMock
            m.ReLU = MagicMock
            m.Sequential = MagicMock
            m.LayerNorm = MagicMock
            m.GELU = MagicMock
        elif module_name == "librosa":
            # Return a valid 2-tuple that matches what load_audio expects
            # waveform (np.ndarray), sample_rate (int)
            import numpy as np
            def mock_load(path, *args, **kwargs):
                if "low_quality" in str(path):
                    # silent waveform -> triggers LowQualityError
                    return (np.zeros(160000), 16000)
                else:
                    # noisy waveform -> passes quality gate
                    return (np.random.normal(0, 0.02, 160000), 16000)
            m.load.side_effect = mock_load

# Execute on import
setup_global_mocks()
