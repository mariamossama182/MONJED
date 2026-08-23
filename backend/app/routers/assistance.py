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


router = APIRouter(
    prefix="/assistance",
    tags=["Assistance & Volunteers"],
)


@router.post(
    "/volunteers",
    response_model=VolunteerRecord,
)
def register_volunteer(
    data: VolunteerInput,
):

    return add_volunteer(data)


@router.post(
    "/requests",
    response_model=AssistanceRequestRecord,
)
def create_request(
    data: AssistanceRequestInput,
):

    return create_assistance_request(data)


@router.get(
    "/requests/pending",
    response_model=list[AssistanceRequestRecord],
)
def pending_requests():

    return get_pending_requests()


@router.post(
    "/requests/{request_id}/match",
    response_model=AssistanceRequestRecord,
)
def match_request(
    request_id: str,
):

    requests = get_pending_requests()

    request = next(
        (
            item
            for item in requests
            if item.request_id == request_id
        ),
        None,
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Pending assistance request not found",
        )

    volunteers = get_available_volunteers(
        request.zone_id
    )

    volunteer = match_volunteer(
        request,
        volunteers,
    )

    if volunteer is None:
        raise HTTPException(
            status_code=404,
            detail="No suitable available volunteer found",
        )

    volunteer.available = False

    assigned = assign_request(
        request_id=request.request_id,
        volunteer_id=volunteer.volunteer_id,
    )

    return assigned