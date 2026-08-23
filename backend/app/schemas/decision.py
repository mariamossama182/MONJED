from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EvidenceType = Literal[
    "flooded_road",
    "blocked_road",
    "rising_water",
    "building_damage",
    "people_trapped",
    "infrastructure_damage",
    "other",
]

RiskLevel = Literal[
    "low",
    "moderate",
    "high",
    "critical",
]

HazardType = Literal[
    "flood",
    "earthquake",
]

DecisionStatus = Literal[
    "normal",
    "action_adjusted",
    "human_review_required",
]


class CommunityEvidence(BaseModel):
    zone_id: str = Field(min_length=1)
    evidence_type: EvidenceType

    description: str = Field(
        min_length=3,
        max_length=500,
    )

    age_minutes: int = Field(ge=0)
    verified: bool = False


class DecisionInput(BaseModel):
    hazard: HazardType
    zone_id: str = Field(min_length=1)

    risk_score: int = Field(
        ge=0,
        le=100,
    )

    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1,
    )

    evidence: list[CommunityEvidence] = Field(
        default_factory=list
    )


class DecisionFromRiskInput(BaseModel):
    hazard: HazardType
    zone_id: str = Field(min_length=1)

    risk_score: int = Field(
        ge=0,
        le=100,
    )

    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1,
    )


class FinalDecision(BaseModel):
    hazard: HazardType
    zone_id: str

    risk_score: int
    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1,
    )

    evidence_used: int = Field(ge=0)

    decision_status: DecisionStatus

    current_action: str
    backup_action: str

    reasons: list[str]

    evaluated_at: datetime
