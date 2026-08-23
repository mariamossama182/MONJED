from datetime import datetime, timezone

from app.schemas.community_report import (
    CommunityReportRecord,
)

from app.schemas.decision import (
    CommunityEvidence,
)


def reports_to_evidence(
    reports: list[CommunityReportRecord],
) -> list[CommunityEvidence]:

    evidence: list[CommunityEvidence] = []

    now = datetime.now(timezone.utc)

    for report in reports:

        age_minutes = max(
            0,
            int(
                (
                    now - report.created_at
                ).total_seconds()
                // 60
            ),
        )

        analysis = report.analysis

        # -------------------------
        # Blocked road
        # -------------------------

        if analysis.blocked_road:

            evidence.append(
                CommunityEvidence(
                    zone_id=report.zone_id,
                    evidence_type="blocked_road",
                    description=report.report_text,
                    age_minutes=age_minutes,
                    verified=report.verified,
                )
            )

        # -------------------------
        # Rising water
        # -------------------------

        if analysis.rising_water:

            evidence.append(
                CommunityEvidence(
                    zone_id=report.zone_id,
                    evidence_type="rising_water",
                    description=report.report_text,
                    age_minutes=age_minutes,
                    verified=report.verified,
                )
            )

        # -------------------------
        # No operational evidence
        # -------------------------

        if (
            not analysis.blocked_road
            and not analysis.rising_water
        ):

            evidence.append(
                CommunityEvidence(
                    zone_id=report.zone_id,
                    evidence_type="other",
                    description=report.report_text,
                    age_minutes=age_minutes,
                    verified=report.verified,
                )
            )

    return evidence