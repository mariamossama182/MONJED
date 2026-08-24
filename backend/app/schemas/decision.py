from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# TYPES
# ============================================================

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
    "no_adjustment",
    "action_adjusted",
    "human_review_required",
]


# ============================================================
# COMMUNITY EVIDENCE
# ============================================================

class CommunityEvidence(BaseModel):
    """
    Operational evidence derived from community reports.

    Community evidence may influence operational decisions,
    but it does NOT modify the scientific risk score.
    """

    zone_id: str = Field(
        min_length=1
    )

    evidence_type: EvidenceType

    description: str = Field(
        min_length=3,
        max_length=500,
    )

    age_minutes: int = Field(
        ge=0
    )

    verified: bool = False


# ============================================================
# DECISION INPUT
# ============================================================

class DecisionInput(BaseModel):
    """
    Input to the deterministic Decision Engine.
    """

    hazard: HazardType

    zone_id: str = Field(
        min_length=1
    )

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


# ============================================================
# DECISION FROM EXISTING RISK
# ============================================================

class DecisionFromRiskInput(BaseModel):
    """
    Risk assessment supplied to the Decision Engine.

    Recent community evidence is retrieved separately
    by the backend using the zone_id.
    """

    hazard: HazardType

    zone_id: str = Field(
        min_length=1
    )

    risk_score: int = Field(
        ge=0,
        le=100,
    )

    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1,
    )


# ============================================================
# FINAL OPERATIONAL DECISION
# ============================================================

class FinalDecision(BaseModel):
    """
    Deterministic operational decision produced by MONJED.

    Risk values remain protected from modification by
    community evidence, accessibility adaptation, or AI.
    """

    hazard: HazardType

    zone_id: str = Field(
        min_length=1
    )

    risk_score: int = Field(
        ge=0,
        le=100,
    )

    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1,
    )

    evidence_used: int = Field(
        ge=0
    )

    decision_status: DecisionStatus

    current_action: str = Field(
        min_length=1
    )

    backup_action: str = Field(
        min_length=1
    )

    reasons: list[str]

    evaluated_at: datetime