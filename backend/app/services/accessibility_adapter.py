from app.schemas.accessibility import (
    AccessibilityProfile,
    AccessibleActionPlan,
)

from app.schemas.decision import FinalDecision


def adapt_decision_for_accessibility(
    decision: FinalDecision,
    profile: AccessibilityProfile,
) -> AccessibleActionPlan:

    needs = profile.accessibility_needs

    adapted_current_action = decision.current_action
    adapted_backup_action = decision.backup_action

    communication_requirements: list[str] = []

    assistance_required = False

    # -------------------------
    # Mobility accessibility
    # -------------------------

    if "mobility" in needs:

        assistance_required = True

        if decision.hazard == "flood":

            adapted_current_action += (
                " Use an accessible safe route if available. "
                "Do not move through floodwater."
            )

            adapted_backup_action += (
                " If you cannot move safely, remain in the safest "
                "accessible location available and request mobility assistance."
            )

        elif decision.hazard == "earthquake":

            adapted_current_action += (
                " Use an accessible route only if it is safe and not damaged."
            )

            adapted_backup_action += (
                " If you cannot move safely, remain in the safest accessible "
                "location available and request trained assistance."
            )

        communication_requirements.append(
            "Include clear information about accessible movement and assistance."
        )

    # -------------------------
    # Visual accessibility
    # -------------------------

    if "visual" in needs:

        communication_requirements.extend(
            [
                "Use screen-reader-friendly text.",
                "Do not rely on colors, icons, or maps alone.",
                "Describe important directions and actions in text.",
            ]
        )

    # -------------------------
    # Hearing accessibility
    # -------------------------

    if "hearing" in needs:

        communication_requirements.extend(
            [
                "Provide the warning in text form.",
                "Do not rely on sirens or audio alerts alone.",
                "Prefer SMS or visible digital notifications.",
            ]
        )

    # -------------------------
    # Cognitive accessibility
    # -------------------------

    if "cognitive" in needs:

        communication_requirements.extend(
            [
                "Use short and simple sentences.",
                "Present actions step by step.",
                "Avoid technical jargon.",
                "Put the most important action first.",
            ]
        )

    # Remove duplicates while preserving order
    communication_requirements = list(
        dict.fromkeys(communication_requirements)
    )

    return AccessibleActionPlan(
        hazard=decision.hazard,
        zone_id=decision.zone_id,

        accessibility_needs=needs,

        original_current_action=decision.current_action,
        original_backup_action=decision.backup_action,

        adapted_current_action=adapted_current_action,
        adapted_backup_action=adapted_backup_action,

        communication_requirements=communication_requirements,

        assistance_request_recommended=assistance_required,
    )