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
)

from app.services.volunteer_store import (
    add_volunteer,
    get_available_volunteers,
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

    Qualification for a specific assistance request is NOT
    decided here. It is enforced later by the matching engine.
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

    Decision-engine generated requests are created internally
    by MONJED and are not submitted through this endpoint.
    """

    return create_assistance_request(
        data
    )


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
    Return requests that are still waiting for assignment.
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

    Safety rules are enforced by volunteer_matching.py.

    Examples:
    - rescue_support -> trained responder required
    - transportation -> appropriate skill + vehicle required
    - ordinary requests -> suitable volunteer preferred

    MONJED does NOT assign an unqualified fallback volunteer.
    """

    # ========================================================
    # 1. FIND REQUEST
    # ========================================================

    request = get_request(
        request_id
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Assistance request not found."
            ),
        )

    # ========================================================
    # 2. REQUEST MUST STILL BE PENDING
    # ========================================================

    if request.status != "pending":

        raise HTTPException(
            status_code=409,
            detail=(
                "Assistance request is no longer pending "
                "and cannot be matched again."
            ),
        )

    # ========================================================
    # 3. GET AVAILABLE CANDIDATES IN SAME ZONE
    # ========================================================

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

    # ========================================================
    # 4. APPLY SAFETY-AWARE MATCHING
    # ========================================================

    volunteer = match_volunteer(
        request=request,
        volunteers=volunteers,
    )

    if volunteer is None:

        # Give a clearer response for safety-critical cases.
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

    # ========================================================
    # 5. ASSIGN REQUEST FIRST
    #
    # Do not mark the volunteer unavailable before confirming
    # that the request assignment itself succeeded.
    # ========================================================

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

    # ========================================================
    # 6. MARK RESPONDER UNAVAILABLE
    # ========================================================

    volunteer.available = False

    # ========================================================
    # 7. RETURN ASSIGNED REQUEST
    # ========================================================

    return assigned