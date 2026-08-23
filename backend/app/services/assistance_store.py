from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.assistance import (
    AssistanceRequestInput,
    AssistanceRequestRecord,
)


_requests: list[AssistanceRequestRecord] = []


def create_assistance_request(
    data: AssistanceRequestInput,
) -> AssistanceRequestRecord:

    request = AssistanceRequestRecord(
        request_id=str(uuid4()),
        **data.model_dump(),
        status="pending",
        created_at=datetime.now(timezone.utc),
    )

    _requests.append(request)

    return request


def get_request(
    request_id: str,
) -> AssistanceRequestRecord | None:

    for request in _requests:

        if request.request_id == request_id:
            return request

    return None


def get_pending_requests() -> list[AssistanceRequestRecord]:

    return [
        request
        for request in _requests
        if request.status == "pending"
    ]


def assign_request(
    request_id: str,
    volunteer_id: str,
) -> AssistanceRequestRecord | None:

    request = get_request(request_id)

    if request is None:
        return None

    request.status = "assigned"
    request.assigned_volunteer_id = volunteer_id
    request.assigned_at = datetime.now(timezone.utc)

    return request