from fastapi import APIRouter

from app.schemas.decision import (
    DecisionInput,
    DecisionFromRiskInput,
    FinalDecision,
)

from app.engines.decision import evaluate_decision

from app.services.community_report_store import (
    get_recent_reports,
)

from app.services.community_evidence_mapper import (
    reports_to_evidence,
)


router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


# ============================================================
# DIRECT DECISION EVALUATION
# ============================================================

@router.post(
    "/evaluate",
    response_model=FinalDecision,
)
def evaluate_final_decision(
    data: DecisionInput,
) -> FinalDecision:
    """
    Evaluate an operational decision using an existing
    deterministic risk assessment and supplied community
    evidence.

    Community evidence may adjust operational actions,
    but it does not modify the scientific risk score
    or risk level.
    """

    result = evaluate_decision(
        data
    )

    return FinalDecision(
        **result
    )


# ============================================================
# DECISION FROM RISK + STORED COMMUNITY EVIDENCE
# ============================================================

@router.post(
    "/from-risk",
    response_model=FinalDecision,
)
def evaluate_from_risk(
    data: DecisionFromRiskInput,
) -> FinalDecision:
    """
    Build the operational decision from a deterministic
    risk assessment plus recent community evidence stored
    for the same zone.

    Only recent reports are converted into operational
    evidence. They do not alter the original risk score.
    """

    # --------------------------------------------------------
    # 1. Load recent community reports
    # --------------------------------------------------------

    reports = get_recent_reports(
        zone_id=data.zone_id,
        max_age_minutes=180,
    )

    # --------------------------------------------------------
    # 2. Convert reports into operational evidence
    # --------------------------------------------------------

    evidence = reports_to_evidence(
        reports
    )

    # --------------------------------------------------------
    # 3. Build deterministic Decision Engine input
    # --------------------------------------------------------

    decision_input = DecisionInput(
        hazard=data.hazard,
        zone_id=data.zone_id,
        risk_score=data.risk_score,
        risk_level=data.risk_level,
        confidence=data.confidence,
        evidence=evidence,
    )

    # --------------------------------------------------------
    # 4. Evaluate operational decision
    # --------------------------------------------------------

    result = evaluate_decision(
        decision_input
    )

    return FinalDecision(
        **result
    )