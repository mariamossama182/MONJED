from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.assistance import (
    AssistanceRequestInput,
    AssistanceRequestRecord,
)

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
)

from app.services.assistance_store import (
    create_assistance_request,
    get_request,
    get_pending_requests,
    assign_request,
    start_request,
    resolve_request,
)

from app.services.volunteer_store import (
    add_volunteer,
    get_available_volunteers,
    get_volunteer,
    set_volunteer_availability,
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
# REGISTER VOLUNTEER / RESPONDER
# ============================================================

@router.post(
    "/volunteers",
    response_model=VolunteerRecord,
)
def register_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:
    """
    Register a volunteer or trained responder.

    Qualification for a specific request is enforced
    later by the safety-aware matching engine.
    """

    return add_volunteer(
        data
    )


# ============================================================
# CREATE MANUAL ASSISTANCE REQUEST
# ============================================================

@router.post(
    "/requests",
    response_model=AssistanceRequestRecord,
)
def create_request(
    data: AssistanceRequestInput,
) -> AssistanceRequestRecord:
    """
    Create a manually submitted assistance request.

    Requests generated automatically by MONJED's Decision
    Engine are created internally by the backend.
    """

    return create_assistance_request(
        data
    )


# ============================================================
# GET ONE REQUEST
# ============================================================

@router.get(
    "/requests/{request_id}",
    response_model=AssistanceRequestRecord,
)
def read_request(
    request_id: str,
) -> AssistanceRequestRecord:
    """
    Return one assistance request by ID.
    """

    request = get_request(
        request_id
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )

    return request


# ============================================================
# GET PENDING REQUESTS
# ============================================================

@router.get(
    "/requests/pending",
    response_model=list[AssistanceRequestRecord],
)
def pending_requests(
) -> list[AssistanceRequestRecord]:
    """
    Return requests waiting for assignment.
    """

    return get_pending_requests()


# ============================================================
# MATCH ASSISTANCE REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/match",
    response_model=AssistanceRequestRecord,
)
def match_request(
    request_id: str,
) -> AssistanceRequestRecord:
    """
    Match a pending assistance request with a safe,
    eligible volunteer or trained responder.

    MONJED never assigns an unqualified fallback volunteer.
    """

    # --------------------------------------------------------
    # 1. FIND REQUEST
    # --------------------------------------------------------

    request = get_request(
        request_id
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )

    # --------------------------------------------------------
    # 2. REQUEST MUST BE PENDING
    # --------------------------------------------------------

    if request.status != "pending":

        raise HTTPException(
            status_code=409,
            detail=(
                "Assistance request is no longer pending "
                "and cannot be matched again."
            ),
        )

    # --------------------------------------------------------
    # 3. GET AVAILABLE CANDIDATES
    # --------------------------------------------------------

    volunteers = get_available_volunteers(
        request.zone_id
    )

    if not volunteers:

        raise HTTPException(
            status_code=404,
            detail=(
                "No available volunteers or responders "
                "were found in this zone."
            ),
        )

    # --------------------------------------------------------
    # 4. SAFETY-AWARE MATCHING
    # --------------------------------------------------------

    volunteer = match_volunteer(
        request=request,
        volunteers=volunteers,
    )

    if volunteer is None:

        if request.requires_trained_responder:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No suitable trained responder is "
                    "currently available for this request."
                ),
            )

        raise HTTPException(
            status_code=404,
            detail=(
                "No suitable available volunteer or responder "
                "matches the required capabilities."
            ),
        )

    # --------------------------------------------------------
    # 5. ASSIGN REQUEST
    # --------------------------------------------------------

    assigned = assign_request(
        request_id=request.request_id,
        volunteer_id=volunteer.volunteer_id,
    )

    if assigned is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assistance request could not be assigned. "
                "It may have already been processed."
            ),
        )

    # --------------------------------------------------------
    # 6. MARK RESPONDER UNAVAILABLE
    # --------------------------------------------------------

    updated_volunteer = set_volunteer_availability(
        volunteer_id=volunteer.volunteer_id,
        available=False,
    )

    if updated_volunteer is None:

        # This should not normally happen because the volunteer
        # was retrieved from the in-memory store moments earlier.
        raise HTTPException(
            status_code=500,
            detail=(
                "Request was assigned, but responder "
                "availability could not be updated."
            ),
        )

    return assigned


# ============================================================
# START ASSISTANCE REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/start",
    response_model=AssistanceRequestRecord,
)
def start_assistance_request(
    request_id: str,
) -> AssistanceRequestRecord:
    """
    Start an assigned assistance request.

    Valid lifecycle transition:
        assigned -> in_progress
    """

    request = get_request(
        request_id
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )

    if request.status != "assigned":

        raise HTTPException(
            status_code=409,
            detail=(
                "Only an assigned assistance request "
                "can be started."
            ),
        )

    if not request.assigned_volunteer_id:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assistance request has no assigned "
                "volunteer or responder."
            ),
        )

    # Defense in depth:
    # the assigned responder should still exist.
    volunteer = get_volunteer(
        request.assigned_volunteer_id
    )

    if volunteer is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assigned volunteer or responder "
                "could not be found."
            ),
        )

    started = start_request(
        request_id
    )

    if started is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assistance request could not "
                "be started."
            ),
        )

    return started


# ============================================================
# RESOLVE ASSISTANCE REQUEST
# ============================================================

@router.post(
    "/requests/{request_id}/resolve",
    response_model=AssistanceRequestRecord,
)
def resolve_assistance_request(
    request_id: str,
) -> AssistanceRequestRecord:
    """
    Resolve an active assistance request.

    Valid lifecycle transition:
        in_progress -> resolved

    When the request is resolved, the assigned volunteer
    or trained responder becomes available again.
    """

    request = get_request(
        request_id
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )

    if request.status != "in_progress":

        raise HTTPException(
            status_code=409,
            detail=(
                "Only an in-progress assistance request "
                "can be resolved."
            ),
        )

    assigned_volunteer_id = (
        request.assigned_volunteer_id
    )

    if not assigned_volunteer_id:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assistance request has no assigned "
                "volunteer or responder."
            ),
        )

    # --------------------------------------------------------
    # Verify responder still exists before changing lifecycle
    # state so we avoid partial updates.
    # --------------------------------------------------------

    volunteer = get_volunteer(
        assigned_volunteer_id
    )

    if volunteer is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assigned volunteer or responder "
                "could not be found."
            ),
        )

    # --------------------------------------------------------
    # RESOLVE REQUEST
    # --------------------------------------------------------

    resolved = resolve_request(
        request_id
    )

    if resolved is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "The assistance request could not "
                "be resolved."
            ),
        )

    # --------------------------------------------------------
    # RELEASE RESPONDER
    # --------------------------------------------------------

    released_volunteer = (
        set_volunteer_availability(
            volunteer_id=assigned_volunteer_id,
            available=True,
        )
    )

    if released_volunteer is None:

        # Extremely defensive condition for the temporary
        # in-memory implementation.
        raise HTTPException(
            status_code=500,
            detail=(
                "The request was resolved, but responder "
                "availability could not be restored."
            ),
        )

    return resolved