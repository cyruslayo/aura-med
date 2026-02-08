class Tensor:
    def __init__(self, shape):
        self.shape = shape
    
    def __eq__(self, other):
        if hasattr(other, 'shape'):
            return self.shape == other.shape
        return False

def randn(*args):
    return Tensor(args)

def cuda():
    return None

class device:
    pass
