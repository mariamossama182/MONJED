from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.schemas.community_report import (
    AnalysisSource,
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)


_reports: list[CommunityReportRecord] = []



# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    report: CommunityReportInput,
    analysis: CommunityReportAnalysis,
    analysis_source: AnalysisSource,
) -> CommunityReportRecord:


    now = datetime.now(
        timezone.utc
    )


    duplicate_window = (
        now - timedelta(minutes=5)
    )


    zone_id = report.zone_id.strip()

    location = report.location.strip().lower()

    text = report.report_text.strip().lower()



    for existing in _reports:


        if (

            existing.zone_id.strip()
            == zone_id

            and

            existing.location.strip().lower()
            == location

            and

            existing.report_text.strip().lower()
            == text

            and

            existing.latitude
            == report.latitude

            and

            existing.longitude
            == report.longitude

            and

            existing.created_at
            >= duplicate_window

        ):

            return existing



    record = CommunityReportRecord(

        report_id=str(
            uuid4()
        ),


        zone_id=zone_id,


        location=report.location.strip(),


        latitude=report.latitude,


        longitude=report.longitude,


        report_text=report.report_text.strip(),


        analysis=analysis,


        analysis_source=analysis_source,


        verified=False,


        created_at=now,
    )


    _reports.append(
        record
    )


    return record



# ============================================================
# RECENT REPORTS
# ============================================================

def get_recent_reports(
    zone_id: str,
    max_age_minutes: int = 180,
):


    cutoff = (
        datetime.now(timezone.utc)
        -
        timedelta(minutes=max_age_minutes)
    )


    zone_id = zone_id.strip()


    return [

        report

        for report in _reports

        if (

            report.zone_id.strip()
            == zone_id

            and

            report.created_at >= cutoff

        )

    ]



# ============================================================
# CLEAR
# ============================================================

def clear_reports():

    _reports.clear()