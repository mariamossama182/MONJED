from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.schemas.assistance import (
    AssistanceRequestInput,
    AssistanceRequestRecord,
)

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
    VolunteerLoginInput,
    VolunteerPublic,
)

from app.services.assistance_store import (
    create_assistance_request,
    get_request,
    get_pending_requests,
    get_all_requests,
    assign_request,
    start_request,
    resolve_request,
)

from app.services.volunteer_store import (
    add_volunteer,
    get_available_volunteers,
    get_volunteer,
    get_volunteer_by_phone,
    get_all_volunteers,
    set_volunteer_availability,
    to_public,
)

from app.engines.volunteer_matching import (
    match_volunteer,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/assistance",
    tags=["Assistance & Volunteers"],
)


# ============================================================
# HELPERS
# ============================================================

def _get_request_or_404(
    request_id: str,
) -> AssistanceRequestRecord:

    request = get_request(request_id)

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )

    return request


def _requires_trained_responder(
    request: AssistanceRequestRecord,
) -> bool:

    return (
        request.requires_trained_responder
        or request.request_type == "rescue_support"
    )


# ============================================================
# REGISTER / LOGIN / LIST VOLUNTEERS
# ============================================================

@router.post(
    "/volunteers",
    response_model=VolunteerRecord,
)
def register_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:

    if data.phone and get_volunteer_by_phone(data.phone):
        raise HTTPException(
            status_code=409,
            detail="Phone already registered as a volunteer.",
        )

    return add_volunteer(data)


@router.post(
    "/volunteers/login",
    response_model=VolunteerRecord,
)
def login_volunteer(
    data: VolunteerLoginInput,
) -> VolunteerRecord:

    volunteer = get_volunteer_by_phone(data.phone)
    if volunteer is None or (volunteer.password or "") != data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone or password.",
        )
    return volunteer


@router.get(
    "/volunteers",
    response_model=list[VolunteerPublic],
)
def list_volunteers() -> list[VolunteerPublic]:
    return [
        VolunteerPublic(**to_public(v))
        for v in get_all_volunteers()
    ]


@router.post(
    "/volunteers/{volunteer_id}/availability",
    response_model=VolunteerRecord,
)
def update_availability(
    volunteer_id: str,
    available: bool = Query(...),
) -> VolunteerRecord:

    updated = set_volunteer_availability(
        volunteer_id=volunteer_id,
        available=available,
    )
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Volunteer not found.",
        )
    return updated


# ============================================================
# CREATE REQUEST
# ============================================================

@router.post(
    "/requests",
    response_model=AssistanceRequestRecord,
)
def create_request(
    data: AssistanceRequestInput,
) -> AssistanceRequestRecord:

    return create_assistance_request(data)


# ============================================================
# LIST / GET REQUESTS  (static paths before {request_id})
# ============================================================

@router.get(
    "/requests",
    response_model=list[AssistanceRequestRecord],
)
def list_requests():
    return get_all_requests()


@router.get(
    "/requests/pending",
    response_model=list[AssistanceRequestRecord],
)
def pending_requests():
    return get_pending_requests()


@router.get(
    "/requests/{request_id}",
    response_model=AssistanceRequestRecord,
)
def read_request(request_id: str):
    return _get_request_or_404(request_id)


# ============================================================
# MATCH REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/match",
    response_model=AssistanceRequestRecord,
)
def match_request(request_id: str):

    request = _get_request_or_404(request_id)

    if request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Only pending requests can be matched.",
        )

    volunteers = get_available_volunteers(request.zone_id)

    if not volunteers:
        raise HTTPException(
            status_code=404,
            detail="No available responders found in this zone.",
        )

    volunteer = match_volunteer(
        request=request,
        volunteers=volunteers,
    )

    if volunteer is None:
        if _requires_trained_responder(request):
            raise HTTPException(
                status_code=404,
                detail=(
                    "No qualified trained responder "
                    "is currently available."
                ),
            )
        raise HTTPException(
            status_code=404,
            detail=(
                "No qualified volunteer matches "
                "the required capabilities."
            ),
        )

    assigned = assign_request(
        request_id=request.request_id,
        volunteer_id=volunteer.volunteer_id,
    )

    if assigned is None:
        raise HTTPException(
            status_code=409,
            detail="Request assignment failed.",
        )

    updated = set_volunteer_availability(
        volunteer_id=volunteer.volunteer_id,
        available=False,
    )

    if updated is None:
        raise HTTPException(
            status_code=500,
            detail="Responder availability update failed.",
        )

    return assigned


# ============================================================
# START REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/start",
    response_model=AssistanceRequestRecord,
)
def start_assistance_request(request_id: str):

    request = _get_request_or_404(request_id)

    if request.status != "assigned":
        raise HTTPException(
            status_code=409,
            detail="Only assigned requests can be started.",
        )

    if not request.assigned_volunteer_id:
        raise HTTPException(
            status_code=409,
            detail="No responder assigned.",
        )

    volunteer = get_volunteer(request.assigned_volunteer_id)

    if volunteer is None:
        raise HTTPException(
            status_code=409,
            detail="Assigned responder not found.",
        )

    started = start_request(request_id)

    if started is None:
        raise HTTPException(
            status_code=409,
            detail="Request could not be started.",
        )

    return started


# ============================================================
# RESOLVE REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/resolve",
    response_model=AssistanceRequestRecord,
)
def resolve_assistance_request(request_id: str):

    request = _get_request_or_404(request_id)

    # Allow resolve from assigned by auto-starting first.
    if request.status == "assigned":
        started = start_request(request_id)
        if started is None:
            raise HTTPException(
                status_code=409,
                detail="Request could not be started before resolve.",
            )
        request = started

    if request.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Only active requests can be resolved.",
        )

    volunteer_id = request.assigned_volunteer_id

    if not volunteer_id:
        raise HTTPException(
            status_code=409,
            detail="No responder assigned.",
        )

    volunteer = get_volunteer(volunteer_id)

    if volunteer is None:
        raise HTTPException(
            status_code=409,
            detail="Assigned responder not found.",
        )

    resolved = resolve_request(request_id)

    if resolved is None:
        raise HTTPException(
            status_code=409,
            detail="Request could not be resolved.",
        )

    released = set_volunteer_availability(
        volunteer_id=volunteer_id,
        available=True,
    )

    if released is None:
        raise HTTPException(
            status_code=500,
            detail="Responder availability could not be restored.",
        )

    return resolved
