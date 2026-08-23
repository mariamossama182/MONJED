from datetime import datetime

from fastapi import APIRouter, Query

from app.schemas.risk import (
    FloodRiskInput,
    EarthquakeRiskInput,
    RiskAssessment,
)

from app.schemas.decision import (
    DecisionInput,
    FinalDecision,
)

from app.schemas.pipeline import MonjedAssessment

from app.schemas.accessibility import (
    AccessibilityNeed,
    AccessibilityProfile,
)

from app.services.flood_risk import (
    calculate_flood_risk,
)

from app.services.earthquake_risk import (
    calculate_earthquake_risk,
)

from app.services.action_engine import (
    get_flood_actions,
    get_earthquake_actions,
)

from app.services.community_report_store import (
    get_recent_reports,
)

from app.services.community_evidence_mapper import (
    reports_to_evidence,
)

from app.services.accessibility_adapter import (
    adapt_decision_for_accessibility,
)

from app.engines.decision import (
    evaluate_decision,
)


router = APIRouter(
    prefix="/pipeline",
    tags=["MONJED Pipeline"],
)


def build_final_decision(
    risk: RiskAssessment,
) -> FinalDecision:

    reports = get_recent_reports(
        zone_id=risk.zone_id,
        max_age_minutes=180,
    )

    evidence = reports_to_evidence(reports)

    decision_input = DecisionInput(
        hazard=risk.hazard,
        zone_id=risk.zone_id,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence=risk.confidence,
        evidence=evidence,
    )

    return FinalDecision(
    **evaluate_decision(decision_input)
)


def build_accessible_action(
    decision: FinalDecision,
    accessibility_needs: list[AccessibilityNeed] | None,
):

    if not accessibility_needs:
        return None

    profile = AccessibilityProfile(
        accessibility_needs=accessibility_needs
    )

    return adapt_decision_for_accessibility(
        decision=decision,
        profile=profile,
    )


@router.post(
    "/flood",
    response_model=MonjedAssessment,
)
def flood_pipeline(
    data: FloodRiskInput,
    accessibility_needs: list[AccessibilityNeed] | None = Query(
        default=None
    ),
):

    # Risk Engine
    risk_score, risk_level, reasons, confidence = (
        calculate_flood_risk(data)
    )

    current_action, backup_action = get_flood_actions(
        risk_level
    )

    risk_assessment = RiskAssessment(
        hazard="flood",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        current_action=current_action,
        backup_action=backup_action,
        evaluated_at=datetime.utcnow(),
    )


    # Decision Engine
    decision = build_final_decision(
        risk_assessment
    )


    # Accessibility Layer
    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )


    return MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
    )


@router.post(
    "/earthquake",
    response_model=MonjedAssessment,
)
def earthquake_pipeline(
    data: EarthquakeRiskInput,
    accessibility_needs: list[AccessibilityNeed] | None = Query(
        default=None
    ),
):

    # Risk Engine
    risk_score, risk_level, reasons, confidence = (
        calculate_earthquake_risk(data)
    )

    current_action, backup_action = get_earthquake_actions(
        risk_level
    )

    risk_assessment = RiskAssessment(
        hazard="earthquake",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        current_action=current_action,
        backup_action=backup_action,
        evaluated_at=datetime.utcnow(),
    )


    # Decision Engine
    decision = build_final_decision(
        risk_assessment
    )


    # Accessibility Layer
    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )


    return MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
    )