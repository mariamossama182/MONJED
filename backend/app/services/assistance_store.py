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
    Remove empty and duplicate report IDs while
    preserving their original order.
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
    Remove duplicate accessibility needs while
    preserving their original order.
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

    rescue_support requests always require a trained responder.
    """

    request = AssistanceRequestRecord(
        request_id=str(
            uuid4()
        ),

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

        started_at=None,

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

    Active requests are:
    - pending
    - assigned
    - in_progress

    Resolved requests are intentionally excluded so a new
    incident can create a new request later.
    """

    normalized_zone_id = _normalize_zone_id(
        zone_id
    )

    normalized_report_ids = set(
        _normalize_report_ids(
            source_report_ids
        )
    )

    # Without source report IDs we cannot safely identify
    # whether two requests refer to the same incident.
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
    Create an assistance request generated by MONJED's
    deterministic Decision Engine.

    IMPORTANT:
    - Intended for human_review_required decisions.
    - Community reports remain unverified unless separately
      verified.
    - rescue_support always requires a trained responder.
    - Duplicate requests for the same source reports are reused.
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
    # SAFETY DEFENSE IN DEPTH
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

        decision_status="human_review_required",

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

        started_at=None,

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
    Return one assistance request by its ID.
    """

    normalized_request_id = (
        request_id.strip()
    )

    if not normalized_request_id:
        return None

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
    Return assistance requests waiting for assignment.
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
    Assign a pending assistance request to a volunteer
    or trained responder.

    Valid transition:
        pending -> assigned

    Qualification checks must already have been completed
    by volunteer_matching.py.
    """

    request = get_request(
        request_id
    )

    if request is None:
        return None

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
# START REQUEST
# ============================================================

def start_request(
    request_id: str,
) -> AssistanceRequestRecord | None:
    """
    Mark an assigned assistance request as actively
    being handled.

    Valid transition:
        assigned -> in_progress

    A request cannot start unless a volunteer/responder
    has already been assigned.
    """

    request = get_request(
        request_id
    )

    if request is None:
        return None

    if request.status != "assigned":
        return None

    # Defense in depth:
    # assigned requests should always have an assigned responder.
    if not request.assigned_volunteer_id:
        return None

    request.status = "in_progress"

    request.started_at = datetime.now(
        timezone.utc
    )

    return request


# ============================================================
# RESOLVE REQUEST
# ============================================================

def resolve_request(
    request_id: str,
) -> AssistanceRequestRecord | None:
    """
    Mark an active assistance request as resolved.

    Valid transition:
        in_progress -> resolved

    Requests cannot jump directly from pending or assigned
    to resolved.
    """

    request = get_request(
        request_id
    )

    if request is None:
        return None

    if request.status != "in_progress":
        return None

    request.status = "resolved"

    request.resolved_at = datetime.now(
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