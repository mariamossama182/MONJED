from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.schemas.community_report import (
    AnalysisSource,
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)


_reports: list[CommunityReportRecord] = []


def save_report(
    report: CommunityReportInput,
    analysis: CommunityReportAnalysis,
    analysis_source: AnalysisSource,
) -> CommunityReportRecord:
    """
    Store a community report together with its structured
    analysis and the backend-controlled analysis source.

    IMPORTANT:
    - analysis_source describes how the report was analyzed.
    - It does NOT mean the report was verified.
    - verified remains False unless a trusted verification
      process explicitly changes it later.
    """

    now = datetime.now(
        timezone.utc
    )

    # --------------------------------------------------------
    # Prevent accidental duplicate submissions
    # --------------------------------------------------------

    duplicate_window = (
        now
        - timedelta(
            minutes=5
        )
    )

    normalized_zone_id = (
        report.zone_id
        .strip()
    )

    normalized_location = (
        report.location
        .strip()
        .lower()
    )

    normalized_report_text = (
        report.report_text
        .strip()
        .lower()
    )

    for existing in _reports:

        same_report = (
            existing.zone_id.strip()
            == normalized_zone_id

            and existing.location.strip().lower()
            == normalized_location

            and existing.report_text.strip().lower()
            == normalized_report_text

            and existing.created_at
            >= duplicate_window
        )

        if same_report:
            return existing

    # --------------------------------------------------------
    # Create stored report
    # --------------------------------------------------------

    record = CommunityReportRecord(
        report_id=str(
            uuid4()
        ),

        zone_id=report.zone_id,

        location=report.location,

        report_text=report.report_text,

        analysis=analysis,

        analysis_source=analysis_source,

        verified=False,

        created_at=now,
    )

    _reports.append(
        record
    )

    return record


def get_recent_reports(
    zone_id: str,
    max_age_minutes: int = 180,
) -> list[CommunityReportRecord]:
    """
    Return reports from the requested zone that are still
    inside the operational evidence window.
    """

    cutoff = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            minutes=max_age_minutes
        )
    )

    normalized_zone_id = (
        zone_id.strip()
    )

    return [
        report
        for report in _reports
        if (
            report.zone_id.strip()
            == normalized_zone_id
            and report.created_at
            >= cutoff
        )
    ]


def clear_reports() -> None:
    """
    Clear the temporary in-memory report store.

    This exists for development/testing only.
    MongoDB persistence will replace this store later.
    """

    _reports.clear()