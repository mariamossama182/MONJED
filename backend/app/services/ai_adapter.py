"""
Monjed AI - AI Adapter

Converts deterministic MONJED backend assessment
into a safe AI communication payload.

Architecture:

Risk Engine
      ↓
Decision Engine
      ↓
Accessibility Layer
      ↓
AI Adapter
      ↓
Gemini Alert Layer


IMPORTANT:
- AI does NOT calculate risk.
- AI does NOT make decisions.
- AI does NOT modify actions.
- AI only generates human-readable communication.
"""


from copy import deepcopy



SUPPORTED_LANGUAGES = {
    "en",
    "ar",
    "fr",
    "sw",
}


VALID_RISK_LEVELS = {
    "low",
    "moderate",
    "high",
    "critical",
}


VALID_ACCESSIBILITY_NEEDS = {
    "mobility",
    "visual",
    "hearing",
    "cognitive",
}


DEFAULT_COUNTRY = "Egypt"


# ============================================================
# VALIDATION HELPERS
# ============================================================


def _validate_language(
    language: str,
) -> str:

    normalized = (
        str(language)
        .lower()
        .strip()
    )

    return (
        normalized
        if normalized in SUPPORTED_LANGUAGES
        else "en"
    )



def _validate_accessibility_needs(
    accessibility_needs,
):

    if not accessibility_needs:
        return []


    if not isinstance(
        accessibility_needs,
        list,
    ):
        raise TypeError(
            "accessibility_needs must be a list."
        )


    normalized = []


    for need in accessibility_needs:

        value = (
            str(need)
            .lower()
            .strip()
        )


        if value not in VALID_ACCESSIBILITY_NEEDS:

            raise ValueError(
                f"Unsupported accessibility need: {need}"
            )


        if value not in normalized:

            normalized.append(value)


    return normalized



def _validate_risk(
    risk,
):

    risk_level = (
        str(risk.risk_level)
        .lower()
        .strip()
    )


    if risk_level not in VALID_RISK_LEVELS:

        raise ValueError(
            f"Invalid risk level: {risk_level}"
        )


    if not isinstance(
        risk.risk_score,
        (int, float),
    ):

        raise TypeError(
            "risk_score must be numeric."
        )


    if not 0 <= risk.risk_score <= 100:

        raise ValueError(
            "risk_score must be between 0 and 100."
        )


    return risk_level



def _safe_text(
    value,
    default,
):

    if value is None:
        return default

    return value



# ============================================================
# BUILD AI PAYLOAD
# ============================================================


def build_ai_payload(
    assessment,
    accessibility=None,
    language="en",
):

    """
    Convert MONJED backend assessment
    into a controlled AI communication payload.

    Gemini receives ONLY approved backend outputs.
    """


    if not hasattr(
        assessment,
        "risk",
    ):

        raise TypeError(
            "Invalid MONJED assessment object."
        )


    if not hasattr(
        assessment,
        "decision",
    ):

        raise TypeError(
            "Invalid MONJED decision object."
        )



    risk = assessment.risk

    decision = assessment.decision



    risk_level = _validate_risk(
        risk
    )


    language = _validate_language(
        language
    )



    current_action = _safe_text(
        decision.current_action,
        "Follow official safety guidance.",
    )


    backup_action = _safe_text(
        decision.backup_action,
        "Follow local authority instructions.",
    )


    decision_status = _safe_text(
        decision.decision_status,
        "no_adjustment",
    )



    accessibility_needs = []

    accessibility_instructions = []



    if accessibility:


        accessibility_needs = (
            _validate_accessibility_needs(
                accessibility.accessibility_needs
            )
        )


        accessibility_instructions = deepcopy(
            accessibility.communication_requirements
        )


        current_action = _safe_text(
            accessibility.adapted_current_action,
            current_action,
        )


        backup_action = _safe_text(
            accessibility.adapted_backup_action,
            backup_action,
        )



    country = getattr(
        assessment,
        "country",
        None,
    )


    if country is None:

        country = getattr(
            risk,
            "country",
            DEFAULT_COUNTRY,
        )



    return {


        # AI safety metadata
        "source":
            "MONJED_BACKEND",


        "ai_role":
            "communication_only",


        "generated_by":
            "MONJED_DECISION_ENGINE",



        "zone_id":
            risk.zone_id,


        "country":
            country,


        "language":
            language,



        "hazards": [

            {

                "hazard":
                    risk.hazard,


                "risk_score":
                    risk.risk_score,


                "risk_level":
                    risk_level,


                "reasons":
                    deepcopy(
                        risk.reasons
                    ),

            }

        ],



        "community_evidence":

            {

                "matching_reports":
                    max(
                        0,
                        decision.evidence_used,
                    )

            },



        "decision":

            {

                "decision_status":
                    decision_status,


                "current_action":
                    current_action,


                "backup_action":
                    backup_action,


                "accessibility_instructions":
                    accessibility_instructions,

            },



        "accessibility_needs":
            accessibility_needs,



        "confidence":

            {

                "source":
                    "backend",

            },

    }