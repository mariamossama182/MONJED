from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================

class ReportSeverity(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class HazardType(str, Enum):
    flood = "flood"
    earthquake = "earthquake"
    unknown = "unknown"


class AnalysisSource(str, Enum):
    """
    Identifies which backend analysis path produced
    the structured community-report analysis.

    IMPORTANT:
    This indicates the analysis mechanism only.
    It does NOT indicate that the report was verified.
    """

    GEMINI = "GEMINI"
    DETERMINISTIC_FALLBACK = "DETERMINISTIC_FALLBACK"


# ============================================================
# COMMUNITY REPORT INPUT
# ============================================================

class CommunityReportInput(BaseModel):
    """
    Raw community report submitted to MONJED.

    The report is analyzed before being converted into
    operational evidence for the Decision Engine.
    """

    report_text: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description=(
            "Free-text community report describing "
            "the local situation"
        ),
    )

    zone_id: str = Field(
        ...,
        min_length=1,
        description="MONJED zone identifier",
    )

    location: str = Field(
        ...,
        min_length=2,
        description=(
            "Location where the situation was reported"
        ),
    )


# ============================================================
# COMMUNITY REPORT ANALYSIS
# ============================================================

class CommunityReportAnalysis(BaseModel):
    """
    Structured interpretation of a community report.

    IMPORTANT:
    - These fields represent information extracted from
      the submitted report.
    - They do NOT automatically mean the information
      has been independently verified.
    - analysis_confidence describes confidence in the
      extraction/interpretation, not confidence that
      the reported event is objectively true.
    """

    hazard_type: HazardType

    severity: ReportSeverity

    # --------------------------------------------------------
    # Flood / route evidence
    # --------------------------------------------------------

    rising_water: bool = False

    blocked_road: bool = False

    # --------------------------------------------------------
    # Earthquake / structural evidence
    # --------------------------------------------------------

    building_damage: bool = False

    infrastructure_damage: bool = False

    # --------------------------------------------------------
    # Human safety / assistance evidence
    # --------------------------------------------------------

    people_trapped: bool = False

    transportation_needed: bool = False

    help_needed: bool = False

    mobility_assistance_needed: bool = False

    # --------------------------------------------------------
    # Analysis metadata
    # --------------------------------------------------------

    analysis_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Confidence in understanding and extracting "
            "information from the report; this is not "
            "verification of the report's truth."
        ),
    )

    extracted_evidence: list[str] = Field(
        default_factory=list
    )


# ============================================================
# STORED COMMUNITY REPORT
# ============================================================

class CommunityReportRecord(BaseModel):
    """
    Community report stored by MONJED.

    IMPORTANT:
    - analysis_source identifies how the structured
      analysis was produced.
    - analysis_source does NOT indicate verification.
    - verified=False means the report has not been
      independently confirmed by an authorized or
      trusted source.
    """

    report_id: str

    zone_id: str

    location: str

    report_text: str

    analysis: CommunityReportAnalysis

    analysis_source: AnalysisSource = Field(
        ...,
        description=(
            "Backend mechanism that produced the structured "
            "analysis. This does not verify the report."
        ),
    )

    verified: bool = False

    created_at: datetime