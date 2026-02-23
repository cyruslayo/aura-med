from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
from pydantic import BaseModel, Field

class TriageStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    INCONCLUSIVE = "INCONCLUSIVE"

class AgeGroup(str, Enum):
    INFANT = "INFANT"            # 0-1 mo
    YOUNG_CHILD = "YOUNG_CHILD"  # 2-11 mo
    CHILD = "CHILD"              # 12-59 mo (5 yr)
    ADOLESCENT = "ADOLESCENT"    # 5-18 yr
    ADULT = "ADULT"              # 19-64 yr
    ELDERLY = "ELDERLY"          # 65+ yr

def get_age_group(age_months: int) -> AgeGroup:
    """Classify age in months into clinical age groups."""
    if age_months < 2: return AgeGroup.INFANT
    if age_months < 12: return AgeGroup.YOUNG_CHILD
    if age_months < 60: return AgeGroup.CHILD
    if age_months < 228: return AgeGroup.ADOLESCENT
    if age_months < 780: return AgeGroup.ADULT
    return AgeGroup.ELDERLY

def get_fast_breathing_threshold(age_months: int) -> int:
    """
    Get the WHO-standard fast breathing threshold (bpm) for a given age.
    Sources: WHO IMCI (Children), WHO IMAI (Adults).
    """
    group = get_age_group(age_months)
    if group == AgeGroup.INFANT: return 60
    if group == AgeGroup.YOUNG_CHILD: return 50
    if group == AgeGroup.CHILD: return 40
    if group == AgeGroup.ADOLESCENT: return 30
    return 20  # Adult/Elderly threshold

def is_pediatric(age_months: int) -> bool:
    """Check if patient is within standard pediatric range (0-18 years)."""
    return age_months < 228

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

