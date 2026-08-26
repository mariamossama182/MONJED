"""
MONJED AI - Deterministic Decision Engine


Architecture:

Risk Engine
      |
      ↓
Decision Engine
      |
      ↓
AI Communication


Responsibilities:
- Evaluate operational situation.
- Combine risk assessment with community evidence.
- Select appropriate operational action.
- Decide whether notification is required.


IMPORTANT:
- Does NOT calculate risk.
- Does NOT modify risk score.
- Does NOT generate alerts.
- Decisions are deterministic and explainable.
"""


from datetime import datetime, timezone


from backend.app.schemas.decision import (
    DecisionInput,
    FinalDecision,
)



# ============================================================
# CONSTANTS
# ============================================================


HIGH_PRIORITY_EVIDENCE = {

    "people_trapped",

    "building_damage",

    "infrastructure_damage",

}



ACTION_EVIDENCE = {

    "blocked_road",

    "rising_water",

}



# ============================================================
# HELPERS
# ============================================================


def _has_evidence_type(
    evidence,
    evidence_types,
):
    """
    Check whether operational evidence exists.
    """

    return any(

        item.evidence_type in evidence_types

        for item in evidence

    )




def _base_actions(
    hazard,
):
    """
    Default actions based on hazard type.
    """


    if hazard == "flood":

        return {

            "current":
                "Monitor water levels and follow official safety guidance.",


            "backup":
                "Avoid flooded roads and do not cross moving water.",

        }



    if hazard == "earthquake":

        return {

            "current":
                "Move away from unsafe structures and follow emergency guidance.",


            "backup":
                "Avoid damaged buildings and exposed areas.",

        }



    return {

        "current":
            "Follow official safety guidance.",


        "backup":
            "Stay alert for updates.",

    }





# ============================================================
# MAIN DECISION FUNCTION
# ============================================================


def generate_decision(
    decision_input: DecisionInput,
) -> FinalDecision:
    """
    Generate deterministic operational decision.

    Community evidence affects:
    - action
    - urgency
    - human review requirement
    - notification requirement


    Community evidence does NOT affect:
    - risk_score
    - risk_level
    """


    actions = _base_actions(
        decision_input.hazard
    )


    evidence = decision_input.evidence


    reasons = []


    status = "no_adjustment"


    notification_required = False


    current_action = actions["current"]


    backup_action = actions["backup"]



    # ========================================================
    # 1. HUMAN REVIEW REQUIRED
    # ========================================================


    if _has_evidence_type(

        evidence,

        HIGH_PRIORITY_EVIDENCE,

    ):


        status = "human_review_required"


        notification_required = True



        current_action = (

            "Immediate human assessment is required "
            "due to severe community impact."

        )



        reasons.append(

            "High-priority community evidence detected."

        )



    # ========================================================
    # 2. ACTION ADJUSTMENT REQUIRED
    # ========================================================


    elif (

        decision_input.risk_level

        in

        {

            "high",

            "critical",

        }

        or

        _has_evidence_type(

            evidence,

            ACTION_EVIDENCE,

        )

    ):


        status = "action_adjusted"


        notification_required = True



        if decision_input.hazard == "flood":


            current_action = (

                "Move to a safer elevated area "
                "and avoid affected locations."

            )



        elif decision_input.hazard == "earthquake":


            current_action = (

                "Move to an open safe area "
                "away from damaged structures."

            )



        reasons.append(

            "Risk level or community evidence requires action adjustment."

        )



    # ========================================================
    # 3. LOW RISK / MONITORING
    # ========================================================


    else:


        reasons.append(

            "No operational adjustment required."

        )



    # ========================================================
    # COMMUNITY INFORMATION
    # ========================================================


    if evidence:


        reasons.append(

            f"{len(evidence)} community evidence item(s) considered."

        )



    # ========================================================
    # FINAL DECISION
    # ========================================================


    return FinalDecision(

        hazard=
            decision_input.hazard,


        zone_id=
            decision_input.zone_id,


        risk_score=
            decision_input.risk_score,


        risk_level=
            decision_input.risk_level,


        confidence=
            decision_input.confidence,


        evidence_used=
            len(evidence),


        decision_status=
            status,


        notification_required=
            notification_required,


        current_action=
            current_action,


        backup_action=
            backup_action,


        reasons=
            reasons,


        evaluated_at=
            datetime.now(
                timezone.utc
            ),

    )