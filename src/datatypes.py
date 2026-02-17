from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
from pydantic import BaseModel, Field

class TriageStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    INCONCLUSIVE = "INCONCLUSIVE"

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

class PatientVitals(BaseModel):
    age_months: int = Field(..., ge=0, description="Patient age in months")
    respiratory_rate: int = Field(..., ge=0, description="Breaths per minute")
    danger_signs: bool = Field(False, description="Presence of any general danger signs")
    unable_to_drink: bool = Field(False, description="Unable to drink or breastfeed")
    vomits_everything: bool = Field(False, description="Vomits everything")
    convulsions: bool = Field(False, description="Convulsions during this illness")
    lethargic: bool = Field(False, description="Lethargic or unconscious")

    @property
    def danger_sign_details(self) -> Dict[str, bool]:
        """Returns a dict of active danger signs."""
        fields = ["unable_to_drink", "vomits_everything", "convulsions", "lethargic"]
        # Include the generic flag as well
        details = {"General Danger Sign": self.danger_signs}
        for f in fields:
            details[f.replace("_", " ").capitalize()] = getattr(self, f)
        return {k: v for k, v in details.items() if v}

@dataclass
class TriageResult:
    status: TriageStatus
    confidence: float
    reasoning: str
    usage_stats: Optional[Dict[str, float]] = None
    action_recommendation: Optional[str] = None

