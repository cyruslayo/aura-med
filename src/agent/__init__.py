from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.core import AuraMedAgent
    from src.agent.safety import (
        DangerSignException,
        LowQualityError,
        LowConfidenceError,
        EdgeConstraintViolation,
        SafetyGuard
    )

# Use TYPE_CHECKING for exports intended for static analysis
if TYPE_CHECKING:
    from src.agent.core import AuraMedAgent
    from src.agent.safety import SafetyGuard

# Runtime exports: provide access via full path to avoid eager cycles
# e.g. from src.agent.core import AuraMedAgent should be used by callers

__all__ = [
    "AuraMedAgent",
    "DangerSignException",
    "LowQualityError",
    "LowConfidenceError",
    "EdgeConstraintViolation",
    "SafetyGuard",
]
