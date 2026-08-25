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
# NORMALIZATION HELPERS
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
    Remove empty and duplicated report IDs.
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
    Create manually submitted assistance request.

    rescue_support always requires trained responder.
    """

    now = datetime.now(
        timezone.utc
    )


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


        # -------------------------
        # GPS LOCATION
        # -------------------------

        latitude=data.latitude,

        longitude=data.longitude,


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


        created_at=now,


        assigned_at=None,

        started_at=None,

        resolved_at=None,
    )


    _requests.append(
        request
    )


    return request



# ============================================================
# FIND EXISTING DECISION REQUEST
# ============================================================

def _find_existing_decision_request(
    *,
    zone_id: str,
    hazard: HazardType,
    request_type: RequestType,
    source_report_ids: list[str],
) -> AssistanceRequestRecord | None:
    """
    Prevent duplicate Decision Engine requests.
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
            request.zone_id.strip()
            != normalized_zone_id
        ):
            continue


        if request.hazard != hazard:
            continue


        if request.request_type != request_type:
            continue


        if (
            set(request.source_report_ids)
            == normalized_report_ids
        ):
            return request


    return None



# ============================================================
# CREATE DECISION ENGINE REQUEST
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

    # NEW GPS SUPPORT
    latitude: float | None = None,
    longitude: float | None = None,

    requires_trained_responder: bool = False,

) -> AssistanceRequestRecord:
    """
    Create MONJED generated assistance request.

    GPS is optional and used later for:
    - frontend maps
    - responder distance ranking
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



    trained_required = (
        requires_trained_responder
        or request_type == "rescue_support"
    )



    existing = _find_existing_decision_request(
        zone_id=zone_id,
        hazard=hazard,
        request_type=request_type,
        source_report_ids=normalized_report_ids,
    )


    if existing is not None:
        return existing



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


        # GPS
        latitude=latitude,

        longitude=longitude,


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


        source_report_ids=normalized_report_ids,


        accessibility_needs=normalized_needs,


        requires_trained_responder=trained_required,


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


    request_id = request_id.strip()


    if not request_id:
        return None


    for request in _requests:

        if request.request_id == request_id:
            return request


    return None



# ============================================================
# GET PENDING REQUESTS
# ============================================================

def get_pending_requests():

    return [
        request
        for request in _requests
        if request.status == "pending"
    ]



# ============================================================
# GET ALL REQUESTS
# ============================================================

def get_all_requests():

    return list(
        _requests
    )



# ============================================================
# ASSIGN REQUEST
# ============================================================

def assign_request(
    request_id: str,
    volunteer_id: str,
):

    request = get_request(
        request_id
    )


    if request is None:
        return None


    if request.status != "pending":
        return None


    volunteer_id = volunteer_id.strip()


    if not volunteer_id:
        return None


    request.status = "assigned"


    request.assigned_volunteer_id = volunteer_id


    request.assigned_at = datetime.now(
        timezone.utc
    )


    return request



# ============================================================
# START REQUEST
# ============================================================

def start_request(
    request_id: str,
):

    request = get_request(
        request_id
    )


    if request is None:
        return None


    if request.status != "assigned":
        return None


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
):

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

def clear_requests():

    _requests.clear()