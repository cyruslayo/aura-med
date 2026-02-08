from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
from pydantic import BaseModel, Field

class TriageStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    INCONCLUSIVE = "INCONCLUSIVE"

class PatientVitals(BaseModel):
    age_months: int = Field(..., ge=0, description="Patient age in months")
    respiratory_rate: int = Field(..., ge=0, description="Breaths per minute")
    danger_signs: bool = Field(False, description="Presence of any general danger signs")

@dataclass
class TriageResult:
    status: TriageStatus
    confidence: float
    reasoning: str
    usage_stats: Optional[Dict[str, float]] = None
    action_recommendation: Optional[str] = None
