from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)


_reports: list[CommunityReportRecord] = []


def save_report(
    report: CommunityReportInput,
    analysis: CommunityReportAnalysis,
) -> CommunityReportRecord:

    now = datetime.now(timezone.utc)

    # Prevent accidental duplicate submissions
    duplicate_window = now - timedelta(minutes=5)

    for existing in _reports:

        same_report = (
            existing.zone_id == report.zone_id
            and existing.location.strip().lower()
            == report.location.strip().lower()
            and existing.report_text.strip().lower()
            == report.report_text.strip().lower()
            and existing.created_at >= duplicate_window
        )

        if same_report:
            return existing

    record = CommunityReportRecord(
        report_id=str(uuid4()),
        zone_id=report.zone_id,
        location=report.location,
        report_text=report.report_text,
        analysis=analysis,
        verified=False,
        created_at=now,
    )

    _reports.append(record)

    return record


def get_recent_reports(
    zone_id: str,
    max_age_minutes: int = 180,
) -> list[CommunityReportRecord]:

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(minutes=max_age_minutes)
    )

    return [
        report
        for report in _reports
        if report.zone_id == zone_id
        and report.created_at >= cutoff
    ]


def clear_reports() -> None:
    _reports.clear()