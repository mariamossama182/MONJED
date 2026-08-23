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


@router.post(
    "/analyze",
    response_model=CommunityReportAnalysis,
)
def analyze_report(
    report: CommunityReportInput,
):
    return analyze_community_report(report)


@router.post(
    "/submit",
    response_model=CommunityReportRecord,
)
def submit_report(
    report: CommunityReportInput,
):
    analysis = analyze_community_report(report)

    return save_report(
        report=report,
        analysis=analysis,
    )


@router.get(
    "/recent/{zone_id}",
    response_model=list[CommunityReportRecord],
)
def recent_reports(
    zone_id: str,
):
    return get_recent_reports(
        zone_id=zone_id,
    )