from uuid import uuid4

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
)


# ============================================================
# TEMPORARY IN-MEMORY STORE
# ============================================================

_volunteers: list[VolunteerRecord] = []


# ============================================================
# ADD VOLUNTEER / RESPONDER
# ============================================================

def add_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:
    """
    Register a volunteer or trained responder.

    responder_level and skills are validated by the
    VolunteerInput schema before reaching this function.
    """

    volunteer_data = data.model_dump()

    # Keep zone identifiers consistent for matching.
    volunteer_data["zone_id"] = (
        data.zone_id.strip()
    )

    volunteer = VolunteerRecord(
        volunteer_id=str(
            uuid4()
        ),
        **volunteer_data,
    )

    _volunteers.append(
        volunteer
    )

    return volunteer


# ============================================================
# AVAILABLE VOLUNTEERS
# ============================================================

def get_available_volunteers(
    zone_id: str,
) -> list[VolunteerRecord]:
    """
    Return available volunteers/responders in the same
    MONJED operational zone.

    Qualification and safety filtering are intentionally
    handled by volunteer_matching.py.
    """

    normalized_zone_id = (
        zone_id.strip()
    )

    return [
        volunteer
        for volunteer in _volunteers
        if (
            volunteer.available
            and volunteer.zone_id.strip()
            == normalized_zone_id
        )
    ]


# ============================================================
# ALL VOLUNTEERS
# ============================================================

def get_all_volunteers() -> list[VolunteerRecord]:
    """
    Return a snapshot of all registered volunteers/responders.
    """

    return list(
        _volunteers
    )


# ============================================================
# CLEAR STORE
# ============================================================

def clear_volunteers() -> None:
    """
    Clear the temporary in-memory volunteer store.

    Intended for development/testing only.
    MongoDB persistence will replace this later.
    """

    _volunteers.clear()