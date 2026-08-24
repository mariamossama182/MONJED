from app.schemas.assistance import (
    AssistanceRequestRecord,
)

from app.schemas.volunteer import (
    VolunteerRecord,
)


# ============================================================
# SKILL REQUIREMENTS
# ============================================================

SKILL_MAPPING: dict[str, tuple[str, ...]] = {
    "evacuation": (
        "evacuation",
        "transportation",
    ),

    "transportation": (
        "transportation",
    ),

    "mobility_assistance": (
        "mobility_assistance",
    ),

    "medical_support": (
        "medical_support",
    ),

    "rescue_support": (
        "rescue_support",
    ),

    "other": (
        "general_support",
    ),
}


# ============================================================
# HELPERS
# ============================================================

def _same_zone(
    volunteer: VolunteerRecord,
    request: AssistanceRequestRecord,
) -> bool:
    """
    Compare MONJED zone identifiers safely.
    """

    return (
        volunteer.zone_id.strip()
        == request.zone_id.strip()
    )


def _requires_trained_responder(
    request: AssistanceRequestRecord,
) -> bool:
    """
    Determine whether a request must only be handled by
    a trained responder.

    Defense in depth:
    rescue_support is always treated as requiring trained
    response even if request metadata was created incorrectly.
    """

    return (
        request.requires_trained_responder
        or request.request_type == "rescue_support"
    )


def _has_required_transport(
    volunteer: VolunteerRecord,
) -> bool:
    """
    Transportation support requires an actual declared vehicle.
    """

    if volunteer.vehicle_type is None:
        return False

    return bool(
        volunteer.vehicle_type.strip()
    )


def _can_use_skill(
    volunteer: VolunteerRecord,
    request: AssistanceRequestRecord,
    skill: str,
) -> bool:
    """
    Validate both the skill and any capability required
    to use that skill safely.
    """

    if skill not in volunteer.skills:
        return False

    # Transportation requests require an actual vehicle.
    if (
        request.request_type == "transportation"
        and skill == "transportation"
    ):
        return _has_required_transport(
            volunteer
        )

    # For evacuation, a transportation-skilled responder
    # can be used only if they actually have a vehicle.
    #
    # A person with the dedicated "evacuation" skill does
    # not necessarily require a vehicle.
    if (
        request.request_type == "evacuation"
        and skill == "transportation"
    ):
        return _has_required_transport(
            volunteer
        )

    return True


# ============================================================
# VOLUNTEER / RESPONDER MATCHING
# ============================================================

def match_volunteer(
    request: AssistanceRequestRecord,
    volunteers: list[VolunteerRecord],
) -> VolunteerRecord | None:
    """
    Find a safe eligible volunteer/responder.

    Matching requirements:

    1. Volunteer must be available.
    2. Volunteer must be in the same MONJED zone.
    3. Safety-critical requests must use a trained responder.
    4. Volunteer must have a relevant skill.
    5. Transportation-based matches require a declared vehicle.

    IMPORTANT:
    There is intentionally NO unqualified fallback candidate.

    If no safe match exists, return None so the request remains
    pending for escalation rather than assigning an unsuitable
    volunteer.
    """

    required_skills = SKILL_MAPPING.get(
        request.request_type,
        (),
    )

    # --------------------------------------------------------
    # BASE ELIGIBILITY
    # --------------------------------------------------------

    candidates = [
        volunteer
        for volunteer in volunteers
        if (
            volunteer.available
            and _same_zone(
                volunteer,
                request,
            )
        )
    ]

    if not candidates:
        return None

    # --------------------------------------------------------
    # TRAINED RESPONDER SAFETY FILTER
    # --------------------------------------------------------

    trained_required = (
        _requires_trained_responder(
            request
        )
    )

    if trained_required:

        candidates = [
            volunteer
            for volunteer in candidates
            if (
                volunteer.responder_level
                == "trained_responder"
            )
        ]

        if not candidates:
            return None

    else:

        # Preserve trained responders for emergencies when
        # ordinary volunteers can safely handle the request.
        candidates = sorted(
            candidates,
            key=lambda volunteer: (
                volunteer.responder_level
                == "trained_responder"
            ),
        )

    # --------------------------------------------------------
    # SKILL MATCHING
    # --------------------------------------------------------

    for required_skill in required_skills:

        for volunteer in candidates:

            if _can_use_skill(
                volunteer,
                request,
                required_skill,
            ):

                return volunteer

    # --------------------------------------------------------
    # NO SAFE MATCH
    # --------------------------------------------------------

    return None