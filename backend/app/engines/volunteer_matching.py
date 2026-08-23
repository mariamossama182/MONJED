from app.schemas.assistance import (
    AssistanceRequestRecord,
)

from app.schemas.volunteer import (
    VolunteerRecord,
)


SKILL_MAPPING = {
    "evacuation": [
        "evacuation",
        "transportation",
    ],

    "transportation": [
        "transportation",
    ],

    "mobility_assistance": [
        "mobility_assistance",
        "first_aid",
    ],

    "medical_support": [
        "first_aid",
        "medical",
    ],

    "rescue_support": [
        "rescue",
        "first_aid",
    ],

    "other": [],
}


def match_volunteer(
    request: AssistanceRequestRecord,
    volunteers: list[VolunteerRecord],
) -> VolunteerRecord | None:

    required_skills = SKILL_MAPPING.get(
        request.request_type,
        [],
    )

    # Same zone + available
    candidates = [
        volunteer
        for volunteer in volunteers
        if volunteer.available
        and volunteer.zone_id == request.zone_id
    ]

    if not candidates:
        return None

    # Prefer volunteers with relevant skills
    if required_skills:

        skilled_candidates = [
            volunteer
            for volunteer in candidates
            if any(
                skill in volunteer.skills
                for skill in required_skills
            )
        ]

        if skilled_candidates:
            return skilled_candidates[0]

    # Fallback candidate
    return candidates[0]