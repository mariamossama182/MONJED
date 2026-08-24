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


# ============================================================
# VALIDATION
# ============================================================

def _validate_accessibility_needs(
    accessibility_needs
):

    if not accessibility_needs:
        return []

    if not isinstance(
        accessibility_needs,
        list
    ):
        raise TypeError(
            "accessibility_needs must be a list."
        )

    normalized = []

    for need in accessibility_needs:

        value = str(
            need
        ).lower().strip()


        if value not in VALID_ACCESSIBILITY_NEEDS:
            raise ValueError(
                f"Unsupported accessibility need: {need}"
            )


        if value not in normalized:
            normalized.append(
                value
            )


    return normalized



# ============================================================
# BUILD AI PAYLOAD
# ============================================================

def build_ai_payload(
    assessment,
    accessibility=None,
    language="en",
):
    """
    Convert MONJED assessment into AI payload.

    AI receives only approved backend outputs.
    """


    risk = assessment.risk
    decision = assessment.decision

    effective_current_action = (
    decision.current_action
    )

    effective_backup_action = (
        decision.backup_action
    )

    # -------------------------
    # Language
    # -------------------------

    language = str(
        language
    ).lower().strip()


    if language not in SUPPORTED_LANGUAGES:
        language = "en"



    # -------------------------
    # Risk validation
    # -------------------------

    risk_level = str(
        risk.risk_level
    ).lower().strip()


    if risk_level not in VALID_RISK_LEVELS:

        raise ValueError(
            f"Invalid risk level: {risk_level}"
        )


    if not isinstance(
        risk.risk_score,
        (int, float)
    ):

        raise TypeError(
            "risk_score must be numeric."
        )



        # -------------------------
    # Accessibility
    # -------------------------

    accessibility_needs = []

    accessibility_instructions = []

    # Default effective actions are the original
    # deterministic Decision Engine actions.
    effective_current_action = (
        decision.current_action
    )

    effective_backup_action = (
        decision.backup_action
    )

    # If accessibility adaptation exists,
    # use the backend-approved adapted actions.
    if accessibility:

        accessibility_needs = (
            _validate_accessibility_needs(
                accessibility.accessibility_needs
            )
        )

        accessibility_instructions = deepcopy(
            accessibility.communication_requirements
        )

        effective_current_action = (
            accessibility.adapted_current_action
        )

        effective_backup_action = (
            accessibility.adapted_backup_action
        )


    # -------------------------
    # Community Evidence
    # -------------------------

    community_evidence = {
        "matching_reports":
            decision.evidence_used,
    }


    # -------------------------
    # Final AI Payload
    # -------------------------

    return {
        "zone_id":
            risk.zone_id,

        "country":
            "Egypt",

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
            community_evidence,

        "decision": {
            "decision_status":
                decision.decision_status,

            "current_action":
                effective_current_action,

            "backup_action":
                effective_backup_action,

            "accessibility_instructions":
                accessibility_instructions,
        },

        "accessibility_needs":
            accessibility_needs,
    }