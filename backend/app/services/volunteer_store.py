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
# NORMALIZATION HELPERS
# ============================================================

def _normalize_skills(
    skills: list[str],
) -> list[str]:

    return list(
        dict.fromkeys(
            skill.strip()
            for skill in skills
            if skill.strip()
        )
    )



# ============================================================
# ADD VOLUNTEER / RESPONDER
# ============================================================

def add_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:
    """
    Register volunteer or trained responder.

    GPS coordinates are stored for responder matching.
    """


    volunteer_data = data.model_dump()



    # Normalize zone

    volunteer_data["zone_id"] = (
        data.zone_id.strip()
    )



    # Normalize name

    volunteer_data["name"] = (
        data.name.strip()
    )



    # Normalize vehicle

    if data.vehicle_type:

        volunteer_data["vehicle_type"] = (
            data.vehicle_type.strip()
        )



    # Normalize skills

    volunteer_data["skills"] = (
        _normalize_skills(
            data.skills
        )
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
# GET VOLUNTEER
# ============================================================

def get_volunteer(
    volunteer_id: str,
) -> VolunteerRecord | None:


    volunteer_id = (
        volunteer_id.strip()
    )


    if not volunteer_id:

        return None



    for volunteer in _volunteers:

        if volunteer.volunteer_id == volunteer_id:

            return volunteer



    return None



# ============================================================
# AVAILABLE VOLUNTEERS
# ============================================================

def get_available_volunteers(
    zone_id: str,
) -> list[VolunteerRecord]:
    """
    Returns available volunteers in same zone.

    Qualification and distance ranking are handled
    by volunteer_matching engine.
    """


    zone_id = zone_id.strip()



    return [

        volunteer

        for volunteer in _volunteers

        if (

            volunteer.available

            and

            volunteer.zone_id.strip()
            ==
            zone_id

        )

    ]



# ============================================================
# UPDATE AVAILABILITY
# ============================================================

def set_volunteer_availability(
    volunteer_id: str,
    available: bool,
) -> VolunteerRecord | None:


    volunteer = get_volunteer(
        volunteer_id
    )


    if volunteer is None:

        return None



    volunteer.available = available


    return volunteer



# ============================================================
# ALL VOLUNTEERS
# ============================================================

def get_all_volunteers():

    return list(
        _volunteers
    )



# ============================================================
# CLEAR STORE
# ============================================================

def clear_volunteers():

    _volunteers.clear()