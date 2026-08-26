from datetime import datetime, timezone

from app.schemas.decision import DecisionInput


# ============================================================
# BASELINE ACTIONS
# ============================================================

def _get_flood_base_actions(
    risk_level: str,
) -> tuple[str, str]:
    """
    Return deterministic baseline flood actions
    based only on the backend risk level.
    """

    if risk_level == "critical":
        return (
            "Move away from flood-prone and low-lying areas "
            "and relocate to a safer elevated location if it "
            "is safe to do so.",
            "If safe movement is not possible, remain in the "
            "safest available elevated location and request "
            "official assistance.",
        )

    if risk_level == "high":
        return (
            "Avoid low-lying areas and floodwater, monitor "
            "official warnings, and prepare to move to a safer "
            "elevated location.",
            "If conditions worsen or access becomes unsafe, "
            "move to the safest available elevated location "
            "and request assistance if needed.",
        )

    if risk_level == "moderate":
        return (
            "Monitor official flood guidance and avoid "
            "low-lying or flood-prone areas.",
            "Be prepared to move to a safer elevated location "
            "if warnings or local conditions worsen.",
        )

    return (
        "Continue monitoring official flood information "
        "and remain aware of changing local conditions.",
        "Avoid floodwater and follow official guidance "
        "if conditions begin to worsen.",
    )


def _get_earthquake_base_actions(
    risk_level: str,
) -> tuple[str, str]:
    """
    Return deterministic post-earthquake impact actions
    based only on the backend risk level.

    MONJED does not predict earthquakes.
    """

    if risk_level == "critical":
        return (
            "Follow official emergency guidance and avoid "
            "damaged buildings, unstable structures, and "
            "other visibly unsafe areas.",
            "Move to a safer open area if it is safe to do so "
            "and request emergency assistance when needed.",
        )

    if risk_level == "high":
        return (
            "Avoid visibly damaged structures and monitor "
            "official earthquake and emergency updates.",
            "Move to a safer open area if the current location "
            "becomes unsafe.",
        )

    if risk_level == "moderate":
        return (
            "Stay alert for hazards, avoid visibly damaged "
            "structures, and monitor official updates.",
            "Move away from unsafe structures if local "
            "conditions deteriorate.",
        )

    return (
        "Monitor official earthquake updates and remain "
        "aware of possible local hazards.",
        "Avoid any structure that appears damaged or unsafe.",
    )


# ============================================================
# DECISION ENGINE
# ============================================================

def evaluate_decision(
    data: DecisionInput,
) -> dict:
    """
    Produce MONJED's deterministic operational decision.

    Responsibilities:
    - Preserve the scientific risk score and risk level.
    - Consider recent community evidence.
    - Adjust operational actions when necessary.
    - Escalate situations requiring human intervention.

    Community evidence does NOT modify:
    - risk_score
    - risk_level

    Gemini is not involved in this decision.
    """


    reasons: list[str] = []

    evidence_used = 0

    blocked_route = False
    people_trapped = False
    severe_damage = False
    rising_water = False

    # ========================================================
    # 1. Analyze Community Evidence
    # ========================================================

    for report in data.evidence:

        # ----------------------------------------------------
        # Ignore evidence from another zone
        # ----------------------------------------------------

        if report.zone_id != data.zone_id:
            continue

        # ----------------------------------------------------
        # Ignore evidence older than 3 hours
        # ----------------------------------------------------

        if report.age_minutes > 180:
            continue

        evidence_used += 1

        # ----------------------------------------------------
        # Blocked / flooded road
        # ----------------------------------------------------

        if report.evidence_type in {
            "blocked_road",
            "flooded_road",
        }:
            blocked_route = True

            reason = (
                "Recent community evidence indicates "
                "a route may be unsafe."
            )

            if reason not in reasons:
                reasons.append(reason)

        # ----------------------------------------------------
        # People trapped
        # ----------------------------------------------------

        elif report.evidence_type == "people_trapped":
            people_trapped = True

            reason = (
                "Recent community evidence indicates "
                "people may require assistance."
            )

            if reason not in reasons:
                reasons.append(reason)

        # ----------------------------------------------------
        # Structural / infrastructure damage
        # ----------------------------------------------------

        elif report.evidence_type in {
            "building_damage",
            "infrastructure_damage",
        }:
            severe_damage = True

            reason = (
                "Recent community evidence indicates "
                "structural or infrastructure damage."
            )

            if reason not in reasons:
                reasons.append(reason)

        # ----------------------------------------------------
        # Rising water
        # ----------------------------------------------------

        elif report.evidence_type == "rising_water":
            rising_water = True

            reason = (
                "Recent community evidence indicates "
                "rising water levels."
            )

            if reason not in reasons:
                reasons.append(reason)


    # ========================================================
    # 3. Baseline Operational Action
    # ========================================================

    if data.hazard == "flood":
        current_action, backup_action = (
            _get_flood_base_actions(
                data.risk_level
            )
        )

    else:
        current_action, backup_action = (
            _get_earthquake_base_actions(
                data.risk_level
            )
        )

    # No community evidence has changed the baseline action yet.
    decision_status = "no_adjustment"

    # High / critical scientific risk independently requires
    # an active notification even when no community reports exist.
    if data.risk_level in {"high", "critical"}:
        decision_status = "action_adjusted"

        reasons.append(
            f"Scientific risk level is {data.risk_level}; "
            "active notification is required."
        )

    # ========================================================
    # 4. Human Escalation
    #
    # Highest priority.
    # ========================================================

    if people_trapped:

        decision_status = "human_review_required"

        current_action = (
            "Request emergency or trained human assistance "
            "for the reported situation."
        )

        backup_action = (
            "Do not attempt unsafe rescue actions. Share the "
            "location and available details with responders."
        )

    # ========================================================
    # 5. Flood Operational Adjustments
    # ========================================================

    elif data.hazard == "flood":

        # Both route blockage and rising water
        if blocked_route and rising_water:

            decision_status = "action_adjusted"

            current_action = (
                "Avoid floodwater and do not use routes "
                "reported as blocked or flooded. Move away "
                "from areas where water levels are rising."
            )

            backup_action = (
                "If no safe route is confirmed, remain in "
                "the safest available elevated location and "
                "request official assistance."
            )

        # Unsafe route only
        elif blocked_route:

            decision_status = "action_adjusted"

            current_action = (
                "Do not use routes reported as blocked or "
                "flooded. Follow verified official guidance "
                "for a safer alternative."
            )

            backup_action = (
                "If no safe route is confirmed, remain in "
                "the safest available location and request "
                "assistance."
            )

        # Rising water only
        elif rising_water:

            decision_status = "action_adjusted"

            current_action = (
                "Avoid floodwater and move away from areas "
                "where water levels are rising."
            )

            backup_action = (
                "If movement is unsafe, remain in the safest "
                "available elevated location and request "
                "assistance."
            )

    # ========================================================
    # 6. Earthquake Operational Adjustments
    # ========================================================

    elif data.hazard == "earthquake":

        # Structural damage + blocked route
        if severe_damage and blocked_route:

            decision_status = "action_adjusted"

            current_action = (
                "Avoid damaged structures and routes reported "
                "as blocked or unsafe. Follow official "
                "emergency guidance."
            )

            backup_action = (
                "Remain in the safest accessible location or "
                "move to a safer open area if it is safe to "
                "do so."
            )

        # Structural damage
        elif severe_damage:

            decision_status = "action_adjusted"

            current_action = (
                "Avoid visibly damaged structures and follow "
                "official emergency guidance."
            )

            backup_action = (
                "Move to a safer accessible open area if it "
                "is safe to do so."
            )

        # Blocked route
        elif blocked_route:

            decision_status = "action_adjusted"

            current_action = (
                "Avoid routes reported as blocked or unsafe "
                "and follow verified official guidance for "
                "a safer alternative."
            )

            backup_action = (
                "If a safe route is not confirmed, remain in "
                "the safest available location until guidance "
                "or assistance is available."
            )

    # ========================================================
    # NOTIFICATION GATE
    # ========================================================

    # Active notification is required when:
    # - scientific risk is high / critical, OR
    # - community evidence adjusted the action, OR
    # - human review is required.
    notification_required = (
        data.risk_level in {"high", "critical"}
        or decision_status in {
            "action_adjusted",
            "human_review_required",
        }
    )

    # ========================================================
    # 7. Explanation When No Adjustment Was Needed
    # ========================================================

    if not reasons:
        reasons.append(
            "No recent community evidence required "
            "an operational action change."
        )

    # ========================================================
    # 8. Final Protected Decision
    # ========================================================

    return {
        "hazard": data.hazard,

        "zone_id": data.zone_id,

        "risk_score": data.risk_score,

        "risk_level": data.risk_level,

        "confidence": data.confidence,

        "evidence_used": evidence_used,

        "decision_status": decision_status,

        "notification_required": notification_required,

        "current_action": current_action,

        "backup_action": backup_action,

        "reasons": reasons,

        "evaluated_at": datetime.now(
            timezone.utc
        ),
    }