from fastapi import APIRouter

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
)

from app.services.community_report_analyzer import (
    analyze_community_report,
)


router = APIRouter(
    prefix="/api/community-reports",
    tags=["Community Reports"],
)


@router.post(
    "/analyze",
    response_model=CommunityReportAnalysis,
)
def analyze_report(report: CommunityReportInput):
    return analyze_community_report(report)