class DangerSignException(Exception):
    """Raised when danger signs are detected, triggering immediate override."""
    pass

class LowQualityError(Exception):
    """Raised when audio quality/duration is insufficient."""
    pass

class LowConfidenceError(Exception):
    """Raised when model confidence is below threshold."""
    pass

class EdgeConstraintViolation(Exception):
    """Raised when resource usage exceeds edge limits."""
    pass
