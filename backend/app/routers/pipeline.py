from datetime import datetime, timezone

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

from app.services.ai_adapter import (
    build_ai_payload,
)

from app.services.gemini_alert import (
    generate_alert,
)


router = APIRouter(
    prefix="/pipeline",
    tags=["MONJED Pipeline"],
)


# ============================================================
# DECISION BUILDER
# ============================================================

def build_final_decision(
    risk: RiskAssessment,
) -> FinalDecision:
    """
    Combine scientific risk assessment with recent
    community evidence to produce the operational decision.

    Community evidence may modify operational actions,
    but it does NOT modify the scientific risk score.
    """

    reports = get_recent_reports(
        zone_id=risk.zone_id,
        max_age_minutes=180,
    )

    evidence = reports_to_evidence(
        reports
    )

    decision_input = DecisionInput(
        hazard=risk.hazard,
        zone_id=risk.zone_id,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence=risk.confidence,
        evidence=evidence,
    )

    decision_result = evaluate_decision(
        decision_input
    )

    return FinalDecision(
        **decision_result
    )


# ============================================================
# ACCESSIBILITY LAYER
# ============================================================

def build_accessible_action(
    decision: FinalDecision,
    accessibility_needs: list[AccessibilityNeed] | None,
):
    """
    Adapt backend-approved actions for accessibility needs.

    Accessibility does NOT modify the risk score or level.
    """

    if not accessibility_needs:
        return None

    profile = AccessibilityProfile(
        accessibility_needs=accessibility_needs
    )

    return adapt_decision_for_accessibility(
        decision=decision,
        profile=profile,
    )


# ============================================================
# AI COMMUNICATION LAYER
# ============================================================

def add_ai_alert(
    assessment: MonjedAssessment,
    accessibility_action=None,
) -> MonjedAssessment:
    """
    Generate a human-readable alert from deterministic
    MONJED backend results.

    Gemini is used only for communication.
    It cannot change risk or operational decisions.
    """

    ai_payload = build_ai_payload(
        assessment=assessment,
        accessibility=accessibility_action,
    )

    ai_alert = generate_alert(
        ai_payload
    )

    return MonjedAssessment(
        risk=assessment.risk,
        decision=assessment.decision,
        accessible_action=assessment.accessible_action,
        ai_alert=ai_alert,
    )


# ============================================================
# FLOOD PIPELINE
# ============================================================

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

    # --------------------------------------------------------
    # 1. Scientific Risk Engine
    # --------------------------------------------------------

    risk_score, risk_level, reasons, confidence = (
        calculate_flood_risk(
            data
        )
    )

    risk_assessment = RiskAssessment(
        hazard="flood",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        evaluated_at=datetime.now(
            timezone.utc
        ),
    )

    # --------------------------------------------------------
    # 2. Operational Decision Engine
    # --------------------------------------------------------

    decision = build_final_decision(
        risk_assessment
    )

    # --------------------------------------------------------
    # 3. Accessibility Layer
    # --------------------------------------------------------

    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )

    # --------------------------------------------------------
    # 4. MONJED Assessment
    # --------------------------------------------------------

    assessment = MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
    )

    # --------------------------------------------------------
    # 5. AI Communication Layer
    # --------------------------------------------------------

    return add_ai_alert(
        assessment,
        accessible_action,
    )


# ============================================================
# EARTHQUAKE PIPELINE
# ============================================================

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

    # --------------------------------------------------------
    # 1. Scientific Risk / Impact Engine
    # --------------------------------------------------------

    risk_score, risk_level, reasons, confidence = (
        calculate_earthquake_risk(
            data
        )
    )

    risk_assessment = RiskAssessment(
        hazard="earthquake",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        evaluated_at=datetime.now(
            timezone.utc
        ),
    )

    # --------------------------------------------------------
    # 2. Operational Decision Engine
    # --------------------------------------------------------

    decision = build_final_decision(
        risk_assessment
    )

    # --------------------------------------------------------
    # 3. Accessibility Layer
    # --------------------------------------------------------

    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )

    # --------------------------------------------------------
    # 4. MONJED Assessment
    # --------------------------------------------------------

    assessment = MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
    )

    # --------------------------------------------------------
    # 5. AI Communication Layer
    # --------------------------------------------------------

    return add_ai_alert(
        assessment,
        accessible_action,
    )