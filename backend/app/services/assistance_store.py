from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.assistance import (
    AccessibilityNeed,
    AssistanceRequestInput,
    AssistanceRequestRecord,
    HazardType,
    RequestPriority,
    RequestType,
)


# ============================================================
# TEMPORARY IN-MEMORY STORE
# ============================================================

_requests: list[AssistanceRequestRecord] = []


# ============================================================
# HELPERS
# ============================================================

def _normalize_zone_id(
    zone_id: str,
) -> str:
    return zone_id.strip()


def _normalize_location(
    location: str,
) -> str:
    return location.strip()


def _normalize_description(
    description: str,
) -> str:
    return description.strip()


def _normalize_report_ids(
    report_ids: list[str],
) -> list[str]:
    """
    Remove empty/duplicate report IDs while preserving order.
    """

    cleaned = [
        report_id.strip()
        for report_id in report_ids
        if report_id.strip()
    ]

    return list(
        dict.fromkeys(cleaned)
    )


def _normalize_accessibility_needs(
    needs: list[AccessibilityNeed],
) -> list[AccessibilityNeed]:
    """
    Remove duplicates while preserving order.
    """

    return list(
        dict.fromkeys(needs)
    )


# ============================================================
# CREATE MANUAL REQUEST
# ============================================================

def create_assistance_request(
    data: AssistanceRequestInput,
) -> AssistanceRequestRecord:
    """
    Create a manually submitted assistance request.

    Manual requests remain separate from requests generated
    automatically by MONJED's deterministic Decision Engine.
    """

    request = AssistanceRequestRecord(
        request_id=str(uuid4()),
        zone_id=_normalize_zone_id(
            data.zone_id
        ),
        location=_normalize_location(
            data.location
        ),
        hazard=data.hazard,
        request_type=data.request_type,
        priority=data.priority,
        description=_normalize_description(
            data.description
        ),
        status="pending",
        assigned_volunteer_id=None,
        source="manual",
        decision_status=None,
        evidence_used=0,
        source_report_ids=[],
        accessibility_needs=[],
        requires_trained_responder=(
            data.request_type == "rescue_support"
        ),
        created_at=datetime.now(
            timezone.utc
        ),
        assigned_at=None,
        resolved_at=None,
    )

    _requests.append(
        request
    )

    return request


# ============================================================
# FIND EXISTING DECISION-ENGINE REQUEST
# ============================================================

def _find_existing_decision_request(
    *,
    zone_id: str,
    hazard: HazardType,
    request_type: RequestType,
    source_report_ids: list[str],
) -> AssistanceRequestRecord | None:
    """
    Prevent duplicate system-generated requests for the
    same underlying community reports.

    Only active requests are considered duplicates.

    We intentionally require source_report_ids for this
    deduplication check so unrelated incidents in the same
    zone are not accidentally merged together.
    """

    normalized_zone_id = _normalize_zone_id(
        zone_id
    )

    normalized_report_ids = set(
        _normalize_report_ids(
            source_report_ids
        )
    )

    if not normalized_report_ids:
        return None

    active_statuses = {
        "pending",
        "assigned",
        "in_progress",
    }

    for request in _requests:

        if request.source != "decision_engine":
            continue

        if request.status not in active_statuses:
            continue

        if (
            _normalize_zone_id(
                request.zone_id
            )
            != normalized_zone_id
        ):
            continue

        if request.hazard != hazard:
            continue

        if request.request_type != request_type:
            continue

        existing_report_ids = set(
            request.source_report_ids
        )

        # Exact incident/report set means the same decision
        # workflow has already generated an assistance request.
        if (
            existing_report_ids
            == normalized_report_ids
        ):
            return request

    return None


# ============================================================
# CREATE DECISION-ENGINE REQUEST
# ============================================================

def create_decision_assistance_request(
    *,
    zone_id: str,
    location: str,
    hazard: HazardType,
    request_type: RequestType,
    priority: RequestPriority,
    description: str,
    evidence_used: int,
    source_report_ids: list[str],
    accessibility_needs: list[AccessibilityNeed] | None = None,
    requires_trained_responder: bool = False,
) -> AssistanceRequestRecord:
    """
    Create an assistance request from MONJED's deterministic
    Decision Engine.

    This function is intended for internal backend use.

    IMPORTANT:
    - Only human_review_required decisions should call this.
    - Community evidence remains unverified unless separately
      verified.
    - rescue_support is always treated as requiring a trained
      responder.
    - Existing requests generated from the same report set are
      reused instead of duplicated.
    """

    if evidence_used < 0:
        raise ValueError(
            "evidence_used cannot be negative."
        )

    normalized_report_ids = (
        _normalize_report_ids(
            source_report_ids
        )
    )

    normalized_needs = (
        _normalize_accessibility_needs(
            accessibility_needs or []
        )
    )

    # --------------------------------------------------------
    # DEFENSE IN DEPTH
    #
    # A rescue request must never be downgraded to an ordinary
    # volunteer task because of an upstream metadata mistake.
    # --------------------------------------------------------

    trained_required = (
        requires_trained_responder
        or request_type == "rescue_support"
    )

    # --------------------------------------------------------
    # IDEMPOTENCY / DUPLICATE PROTECTION
    # --------------------------------------------------------

    existing = _find_existing_decision_request(
        zone_id=zone_id,
        hazard=hazard,
        request_type=request_type,
        source_report_ids=normalized_report_ids,
    )

    if existing is not None:
        return existing

    # --------------------------------------------------------
    # CREATE REQUEST
    # --------------------------------------------------------

    request = AssistanceRequestRecord(
        request_id=str(
            uuid4()
        ),

        zone_id=_normalize_zone_id(
            zone_id
        ),

        location=_normalize_location(
            location
        ),

        hazard=hazard,

        request_type=request_type,

        priority=priority,

        description=_normalize_description(
            description
        ),

        status="pending",

        assigned_volunteer_id=None,

        source="decision_engine",

        decision_status=(
            "human_review_required"
        ),

        evidence_used=evidence_used,

        source_report_ids=(
            normalized_report_ids
        ),

        accessibility_needs=(
            normalized_needs
        ),

        requires_trained_responder=(
            trained_required
        ),

        created_at=datetime.now(
            timezone.utc
        ),

        assigned_at=None,

        resolved_at=None,
    )

    _requests.append(
        request
    )

    return request


# ============================================================
# GET REQUEST
# ============================================================

def get_request(
    request_id: str,
) -> AssistanceRequestRecord | None:
    """
    Return one assistance request by ID.
    """

    normalized_request_id = (
        request_id.strip()
    )

    for request in _requests:

        if (
            request.request_id
            == normalized_request_id
        ):
            return request

    return None


# ============================================================
# GET PENDING REQUESTS
# ============================================================

def get_pending_requests(
) -> list[AssistanceRequestRecord]:
    """
    Return all requests currently waiting for assignment.
    """

    return [
        request
        for request in _requests
        if request.status == "pending"
    ]


# ============================================================
# GET ALL REQUESTS
# ============================================================

def get_all_requests(
) -> list[AssistanceRequestRecord]:
    """
    Return a snapshot of all assistance requests.
    """

    return list(
        _requests
    )


# ============================================================
# ASSIGN REQUEST
# ============================================================

def assign_request(
    request_id: str,
    volunteer_id: str,
) -> AssistanceRequestRecord | None:
    """
    Assign a pending request to a volunteer/responder.

    Qualification checks must happen in volunteer_matching.py
    before this function is called.

    This function protects request lifecycle state and prevents
    accidental reassignment.
    """

    request = get_request(
        request_id
    )

    if request is None:
        return None

    # Only pending requests may be assigned.
    if request.status != "pending":
        return None

    normalized_volunteer_id = (
        volunteer_id.strip()
    )

    if not normalized_volunteer_id:
        return None

    request.status = "assigned"

    request.assigned_volunteer_id = (
        normalized_volunteer_id
    )

    request.assigned_at = datetime.now(
        timezone.utc
    )

    return request


# ============================================================
# CLEAR STORE
# ============================================================

def clear_requests() -> None:
    """
    Clear the temporary in-memory assistance store.

    Development/testing only.
    MongoDB persistence will replace this later.
    """

    _requests.clear()