from fastapi import APIRouter, HTTPException

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
    get_all_reports,
    get_report,
    set_report_verified,
    set_report_resolved,
)


router = APIRouter(
    prefix="/api/community-reports",
    tags=["Community Reports"],
)


@router.post(
    "/analyze",
    response_model=CommunityReportAnalysis,
)
def analyze_report(
    report: CommunityReportInput,
) -> CommunityReportAnalysis:
    analysis, _analysis_source = analyze_community_report(report)
    return analysis


@router.post(
    "/submit",
    response_model=CommunityReportRecord,
)
def submit_report(
    report: CommunityReportInput,
) -> CommunityReportRecord:
    analysis, analysis_source = analyze_community_report(report)
    return save_report(
        report=report,
        analysis=analysis,
        analysis_source=analysis_source,
    )


@router.get(
    "",
    response_model=list[CommunityReportRecord],
)
def list_reports() -> list[CommunityReportRecord]:
    """All stored community reports (newest first)."""
    return get_all_reports()


@router.get(
    "/recent/{zone_id}",
    response_model=list[CommunityReportRecord],
)
def recent_reports(
    zone_id: str,
) -> list[CommunityReportRecord]:
    return get_recent_reports(zone_id=zone_id)


@router.get(
    "/{report_id}",
    response_model=CommunityReportRecord,
)
def read_report(report_id: str) -> CommunityReportRecord:
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@router.post(
    "/{report_id}/verify",
    response_model=CommunityReportRecord,
)
def verify_report(report_id: str) -> CommunityReportRecord:
    updated = set_report_verified(report_id, True)
    if updated is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return updated


@router.post(
    "/{report_id}/resolve",
    response_model=CommunityReportRecord,
)
def resolve_report(report_id: str) -> CommunityReportRecord:
    updated = set_report_resolved(report_id, True)
    if updated is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return updated
