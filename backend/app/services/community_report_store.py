from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.schemas.community_report import (
    AnalysisSource,
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)
from app.services.mongo_store import dump_record, mongo_available, strip_mongo_id


_reports: list[CommunityReportRecord] = []


def _from_doc(doc: dict | None) -> CommunityReportRecord | None:
    clean = strip_mongo_id(doc)
    if not clean:
        return None
    try:
        return CommunityReportRecord.model_validate(clean)
    except Exception:
        return None


def _load_all_mongo() -> list[CommunityReportRecord]:
    from database.reports_repository import get_all_reports as mongo_get_all

    records = []
    for doc in mongo_get_all() or []:
        record = _from_doc(doc)
        if record is not None:
            records.append(record)
    return sorted(records, key=lambda r: r.created_at, reverse=True)


def save_report(
    report: CommunityReportInput,
    analysis: CommunityReportAnalysis,
    analysis_source: AnalysisSource,
) -> CommunityReportRecord:
    now = datetime.now(timezone.utc)
    duplicate_window = now - timedelta(minutes=5)

    zone_id = report.zone_id.strip()
    location = report.location.strip().lower()
    text = report.report_text.strip().lower()

    existing_pool = get_all_reports()
    for existing in existing_pool:
        if (
            existing.zone_id.strip() == zone_id
            and existing.location.strip().lower() == location
            and existing.report_text.strip().lower() == text
            and existing.latitude == report.latitude
            and existing.longitude == report.longitude
            and existing.created_at >= duplicate_window
        ):
            return existing

    record = CommunityReportRecord(
        report_id=str(uuid4()),
        zone_id=zone_id,
        location=report.location.strip(),
        latitude=report.latitude,
        longitude=report.longitude,
        report_text=report.report_text.strip(),
        analysis=analysis,
        analysis_source=analysis_source,
        verified=False,
        resolved=False,
        created_at=now,
    )

    if mongo_available():
        try:
            from database.reports_repository import create_report

            create_report(dump_record(record))
            return record
        except Exception as exc:
            print(f"MONJED report persist warning: {type(exc).__name__}: {exc}")

    _reports.append(record)
    return record


def get_recent_reports(zone_id: str, max_age_minutes: int = 180):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
    zone_id = zone_id.strip()
    return [
        report
        for report in get_all_reports()
        if report.zone_id.strip() == zone_id and report.created_at >= cutoff
    ]


def get_all_reports():
    if mongo_available():
        try:
            return _load_all_mongo()
        except Exception as exc:
            print(f"MONJED report list warning: {type(exc).__name__}: {exc}")
    return sorted(_reports, key=lambda r: r.created_at, reverse=True)


def get_report(report_id: str):
    report_id = (report_id or "").strip()
    if not report_id:
        return None

    if mongo_available():
        try:
            from database.reports_repository import get_report as mongo_get

            record = _from_doc(mongo_get(report_id))
            if record is not None:
                return record
        except Exception as exc:
            print(f"MONJED report get warning: {type(exc).__name__}: {exc}")

    for report in _reports:
        if report.report_id == report_id:
            return report
    return None


def set_report_verified(report_id: str, verified: bool = True):
    report = get_report(report_id)
    if report is None:
        return None
    updated = report.model_copy(update={"verified": verified})

    if mongo_available():
        try:
            from database.reports_repository import update_report

            update_report(report_id, {"verified": verified})
            return updated
        except Exception as exc:
            print(f"MONJED report verify warning: {type(exc).__name__}: {exc}")

    for i, existing in enumerate(_reports):
        if existing.report_id == report_id:
            _reports[i] = updated
            return updated
    _reports.append(updated)
    return updated


def set_report_resolved(report_id: str, resolved: bool = True):
    report = get_report(report_id)
    if report is None:
        return None
    patch = {
        "resolved": resolved,
        "verified": True if resolved else report.verified,
    }
    updated = report.model_copy(update=patch)

    if mongo_available():
        try:
            from database.reports_repository import update_report

            update_report(report_id, patch)
            return updated
        except Exception as exc:
            print(f"MONJED report resolve warning: {type(exc).__name__}: {exc}")

    for i, existing in enumerate(_reports):
        if existing.report_id == report_id:
            _reports[i] = updated
            return updated
    _reports.append(updated)
    return updated


def clear_reports():
    _reports.clear()
    if mongo_available():
        try:
            from database.reports_repository import get_reports_collection

            get_reports_collection().delete_many({})
        except Exception as exc:
            print(f"MONJED report clear warning: {type(exc).__name__}: {exc}")
