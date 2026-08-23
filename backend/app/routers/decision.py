from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.decision import (
    DecisionInput,
    DecisionFromRiskInput,
    FinalDecision,
)

from app.engines.decision import evaluate_decision

from app.services.community_report_store import get_recent_reports
from app.services.community_evidence_mapper import reports_to_evidence


router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


@router.post(
    "/evaluate",
    response_model=FinalDecision,
)
def evaluate_final_decision(
    data: DecisionInput,
) -> FinalDecision:

    result = evaluate_decision(data)

    return FinalDecision(
        hazard=data.hazard,
        zone_id=data.zone_id,
        risk_score=data.risk_score,
        risk_level=data.risk_level,
        confidence=result["confidence"],
        evidence_used=result["evidence_used"],
        decision_status=result["decision_status"],
        current_action=result["current_action"],
        backup_action=result["backup_action"],
        reasons=result["reasons"],
        evaluated_at=datetime.now(timezone.utc),
    )


@router.post(
    "/from-risk",
    response_model=FinalDecision,
)
def evaluate_from_risk(
    data: DecisionFromRiskInput,
) -> FinalDecision:

    reports = get_recent_reports(
        zone_id=data.zone_id,
        max_age_minutes=180,
    )

    evidence = reports_to_evidence(reports)

    decision_input = DecisionInput(
        hazard=data.hazard,
        zone_id=data.zone_id,
        risk_score=data.risk_score,
        risk_level=data.risk_level,
        confidence=data.confidence,
        evidence=evidence,
    )

    result = evaluate_decision(decision_input)

    return FinalDecision(
        hazard=data.hazard,
        zone_id=data.zone_id,
        risk_score=data.risk_score,
        risk_level=data.risk_level,
        confidence=result["confidence"],
        evidence_used=result["evidence_used"],
        decision_status=result["decision_status"],
        current_action=result["current_action"],
        backup_action=result["backup_action"],
        reasons=result["reasons"],
        evaluated_at=datetime.now(timezone.utc),
    )
