from datetime import datetime, timezone
from app.schemas.decision import DecisionInput

def evaluate_decision(data: DecisionInput):

    confidence = data.confidence

    reasons = []

    evidence_used = 0

    blocked_route = False
    people_trapped = False
    severe_damage = False
    rising_water = False

    # --------------------------------
    # Analyze community evidence
    # --------------------------------

    for report in data.evidence:

        # Ignore reports older than 3 hours
        if report.age_minutes > 180:
            continue

        evidence_used += 1

        # Verified evidence gives slightly more confidence
        if report.verified:
            confidence += 0.02

        if report.evidence_type in [
            "blocked_road",
            "flooded_road",
        ]:
            blocked_route = True

            reasons.append(
                "Recent community evidence indicates "
                "a route may be unsafe."
            )

        elif report.evidence_type == "people_trapped":
            people_trapped = True

            reasons.append(
                "Recent community evidence indicates "
                "people may require assistance."
            )

        elif report.evidence_type in [
            "building_damage",
            "infrastructure_damage",
        ]:
            severe_damage = True

            reasons.append(
                "Recent community evidence indicates "
                "structural or infrastructure damage."
            )

        elif report.evidence_type == "rising_water":
            rising_water = True

            reasons.append(
                "Recent community evidence indicates "
                "rising water levels."
            )

    confidence = min(
        round(confidence, 2),
        0.95,
    )

    # --------------------------------
    # Default action
    # --------------------------------

    if data.hazard == "flood":

        current_action = (
            "Monitor official flood guidance "
            "and avoid unsafe low-lying areas."
        )

        backup_action = (
            "Move to a safer elevated location "
            "if conditions worsen."
        )

    else:

        current_action = (
            "Monitor official earthquake updates "
            "and avoid visibly damaged structures."
        )

        backup_action = (
            "Move to a safer open area if the "
            "current location becomes unsafe."
        )

    decision_status = "normal"

    # --------------------------------
    # Blocked / flooded route
    # --------------------------------

    if blocked_route:

        decision_status = "action_adjusted"

        current_action = (
            "Do not use routes reported as blocked "
            "or flooded. Follow verified official "
            "guidance for a safer alternative."
        )

        backup_action = (
            "If no safe route is confirmed, remain "
            "in the safest accessible location and "
            "request assistance."
        )

    # --------------------------------
    # Rising water
    # --------------------------------

    if (
        rising_water
        and data.hazard == "flood"
    ):

        decision_status = "action_adjusted"

        current_action = (
            "Avoid floodwater and move away from "
            "areas where water levels are rising."
        )

        backup_action = (
            "If movement is unsafe, move to the "
            "safest elevated accessible location "
            "and request assistance."
        )

    # --------------------------------
    # Earthquake damage
    # --------------------------------

    if (
        severe_damage
        and data.hazard == "earthquake"
    ):

        decision_status = "action_adjusted"

        current_action = (
            "Avoid visibly damaged structures and "
            "follow official emergency guidance."
        )

        backup_action = (
            "Move to a safer accessible open area "
            "if it is safe to do so."
        )

    # --------------------------------
    # Human escalation
    # --------------------------------

    if people_trapped:

        decision_status = "human_review_required"

        current_action = (
            "Request emergency or trained human "
            "assistance for the reported situation."
        )

        backup_action = (
            "Do not attempt unsafe rescue actions. "
            "Share the location and available details "
            "with responders."
        )

    if not reasons:
        reasons.append(
            "No recent community evidence required "
            "an operational action change."
        )

    return {
    "hazard": data.hazard,
    "zone_id": data.zone_id,

    "risk_score": data.risk_score,
    "risk_level": data.risk_level,

    "confidence": confidence,

    "evidence_used": evidence_used,

    "decision_status": decision_status,

    "current_action": current_action,
    "backup_action": backup_action,

    "reasons": reasons,

    "evaluated_at": datetime.now(timezone.utc),
}