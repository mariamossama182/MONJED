def build_ai_payload(
    assessment,
    accessibility=None,
):
    """
    Converts MONJED assessment output into a structured
    payload for AI alert generation.

    AI does NOT decide risk.
    It only explains and formats the recommended action.
    """

    risk = assessment.risk
    decision = assessment.decision

    accessibility_instructions = []

    if accessibility:
        accessibility_instructions = (
            accessibility.communication_requirements
        )

    return {

        "platform": "MONJED",

        "location": {
            "zone_id": risk.zone_id,
            "country": "Egypt",
        },

        "hazard_assessment": {

            "hazard": risk.hazard,

            "risk_score": risk.risk_score,

            "risk_level": risk.risk_level,

            "confidence": risk.confidence,

            "evidence_reasons": risk.reasons,
        },


        "community_context": {

            "reports_used":
                decision.evidence_used,

            "decision_status":
                decision.decision_status,
        },


        "recommended_action": {

            "primary":
                decision.current_action,

            "backup":
                decision.backup_action,
        },


        "accessibility": {

            "enabled":
                accessibility is not None,

            "instructions":
                accessibility_instructions,
        },


        "constraints": {

            "ai_role":
                "Generate explanation only. Do not change risk level or action.",

            "require_simple_language":
                True,
        }
    }