from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReportSeverity(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class HazardType(str, Enum):
    flood = "flood"
    earthquake = "earthquake"
    unknown = "unknown"


class CommunityReportInput(BaseModel):
    report_text: str = Field(
        ...,
        min_length=3,
        description="Free-text community report describing the local situation",
    )

    zone_id: str = Field(
        ...,
        min_length=1,
        description="MONJED zone identifier",
    )

    location: str = Field(
        ...,
        min_length=2,
        description="Location where the situation was reported",
    )


class CommunityReportAnalysis(BaseModel):
    hazard_type: HazardType

    severity: ReportSeverity

    rising_water: bool = False

    blocked_road: bool = False

    transportation_needed: bool = False

    help_needed: bool = False

    mobility_assistance_needed: bool = False

    analysis_confidence: float = Field(
        ...,
        ge=0,
        le=1,
    )

    extracted_evidence: list[str]


class CommunityReportRecord(BaseModel):
    report_id: str

    zone_id: str
    location: str
    report_text: str

    analysis: CommunityReportAnalysis

    verified: bool = False

    created_at: datetime