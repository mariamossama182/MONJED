from fastapi import APIRouter

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)

from app.services.community_report_analyzer import (
    analyze_community_report,
)

from app.services.community_report_store import (
    save_report,
    get_recent_reports,
)


router = APIRouter(
    prefix="/api/community-reports",
    tags=["Community Reports"],
)


# ============================================================
# ANALYZE REPORT
# ============================================================

@router.post(
    "/analyze",
    response_model=CommunityReportAnalysis,
)
def analyze_report(
    report: CommunityReportInput,
) -> CommunityReportAnalysis:
    """
    Analyze a community report without storing it.

    The public response contains only the structured analysis.

    analysis_source is intentionally not returned here because
    this endpoint's response contract is CommunityReportAnalysis.
    """

    analysis, _analysis_source = (
        analyze_community_report(
            report
        )
    )

    return analysis


# ============================================================
# SUBMIT AND STORE REPORT
# ============================================================

@router.post(
    "/submit",
    response_model=CommunityReportRecord,
)
def submit_report(
    report: CommunityReportInput,
) -> CommunityReportRecord:
    """
    Analyze and store a community report.

    The backend records both:
    - the structured analysis
    - the mechanism that produced that analysis

    analysis_source does NOT indicate that the report
    has been verified.
    """

    analysis, analysis_source = (
        analyze_community_report(
            report
        )
    )

    return save_report(
        report=report,
        analysis=analysis,
        analysis_source=analysis_source,
    )


# ============================================================
# RECENT REPORTS
# ============================================================

@router.get(
    "/recent/{zone_id}",
    response_model=list[CommunityReportRecord],
)
def recent_reports(
    zone_id: str,
) -> list[CommunityReportRecord]:
    """
    Return recently stored community reports for a zone.
    """

    return get_recent_reports(
        zone_id=zone_id,
    )