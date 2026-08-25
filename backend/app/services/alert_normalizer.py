"""
MONJED AI - Alert Normalizer

Converts validated AI alerts into MONJED
delivery format.

Architecture:

Gemini Alert
      |
      ↓
Alert Normalizer
      |
      ↓
Dashboard / SMS / Voice


Rules:
- Does NOT make decisions.
- Does NOT calculate risk.
- Does NOT modify backend actions.
- Backend payload remains the source of truth.
"""


from copy import deepcopy
from datetime import datetime, timezone



# ============================================================
# HELPERS
# ============================================================


def _safe_list(value):

    if isinstance(value, list):
        return value

    return []



def _safe_dict(value):

    if isinstance(value, dict):
        return value

    return {}



def _get_backend_decision(
    backend_payload: dict,
):

    return _safe_dict(
        backend_payload.get(
            "decision",
            {}
        )
    )



def _get_value(
    data: dict,
    primary: str,
    fallback: str,
    default=None,
):

    value = data.get(primary)

    if value is not None:
        return value

    return data.get(
        fallback,
        default
    )



# ============================================================
# HAZARD NORMALIZATION
# ============================================================


def _normalize_hazards(
    ai_alert: dict,
    backend_payload: dict,
):

    normalized = []


    hazards = _safe_list(
        ai_alert.get(
            "hazards",
            []
        )
    )


    if not hazards:

        hazards = _safe_list(
            backend_payload.get(
                "hazards",
                []
            )
        )



    for hazard in hazards:


        if not isinstance(
            hazard,
            dict
        ):
            continue



        reasons = hazard.get(
            "reasons",
            []
        )


        if reasons and isinstance(
            reasons,
            list
        ):

            message = str(
                reasons[0]
            )

        else:

            message = hazard.get(
                "message",
                "Risk detected. Follow safety guidance."
            )



        normalized.append(

            {

                "type":
                    _get_value(
                        hazard,
                        "type",
                        "hazard",
                        "unknown"
                    ),


                "risk_level":
                    _get_value(
                        hazard,
                        "risk_level",
                        "level",
                        "unknown"
                    ),


                "risk_score":
                    _get_value(
                        hazard,
                        "risk_score",
                        "score",
                        0
                    ),


                "confidence":
                    hazard.get(
                        "confidence",
                        ai_alert.get(
                            "confidence"
                        )
                    ),


                "message":
                    message,

            }

        )


    return normalized



# ============================================================
# MAIN NORMALIZER
# ============================================================


def normalize_alert(
    ai_alert: dict,
    backend_payload: dict,
):


    if not isinstance(
        ai_alert,
        dict
    ):

        raise TypeError(
            "ai_alert must be dictionary"
        )



    if not isinstance(
        backend_payload,
        dict
    ):

        raise TypeError(
            "backend_payload must be dictionary"
        )



    backend_decision = _get_backend_decision(
        backend_payload
    )



    generated_at = datetime.now(
        timezone.utc
    ).isoformat()



    return {


        "title":

            ai_alert.get(
                "title",
                "MONJED Alert"
            ),



        "zone_id":

            backend_payload.get(
                "zone_id",
                "UNKNOWN"
            ),



        "country":

            backend_payload.get(
                "country",
                ai_alert.get(
                    "country",
                    "UNKNOWN"
                )
            ),



        "language":

            backend_payload.get(
                "language",
                "en"
            ),



        # Backend controlled timestamp

        "generated_at":

            generated_at,



        "hazards":

            _normalize_hazards(
                ai_alert,
                backend_payload
            ),



        "community_evidence_summary":

            ai_alert.get(
                "summary",
                ""
            ),



        "final_decision":

            {


                "decision_status":

                    backend_decision.get(
                        "decision_status"
                    ),



                "current_action":

                    backend_decision.get(
                        "current_action"
                    ),



                "backup_action":

                    backend_decision.get(
                        "backup_action"
                    ),



                "accessibility_instructions":

                    deepcopy(

                        backend_decision.get(
                            "accessibility_instructions",
                            []
                        )

                    ),

            },



        "accessibility_needs":

            deepcopy(

                backend_payload.get(
                    "accessibility_needs",
                    []
                )

            ),



        "alert_message":

            ai_alert.get(
                "summary",
                ""
            ),



        "alert_source":

            ai_alert.get(
                "alert_source",
                "GEMINI"
            ),


    }