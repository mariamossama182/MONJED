from uuid import uuid4

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
)


_volunteers: list[VolunteerRecord] = []


def add_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:

    volunteer = VolunteerRecord(
        volunteer_id=str(uuid4()),
        **data.model_dump(),
    )

    _volunteers.append(volunteer)

    return volunteer


def get_available_volunteers(
    zone_id: str,
) -> list[VolunteerRecord]:

    return [
        volunteer
        for volunteer in _volunteers
        if volunteer.zone_id == zone_id
        and volunteer.available
    ]


def get_all_volunteers() -> list[VolunteerRecord]:
    return _volunteers