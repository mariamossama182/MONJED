from app.schemas.risk import FloodRiskInput, RiskLevel


def calculate_confidence(data: FloodRiskInput) -> float:
    """
    Prototype evidence-confidence heuristic.

    This is NOT the probability that a flood will happen.
    It represents how complete/recent the evidence is.
    """

    confidence = 0.65

    # Recent data increases confidence
    if data.data_age_minutes <= 60:
        confidence += 0.15
    elif data.data_age_minutes <= 180:
        confidence += 0.05
    elif data.data_age_minutes > 360:
        confidence -= 0.15

    # Previous data allows trend comparison
    if data.previous_rainfall_24h_mm is not None:
        confidence += 0.10

    # Community evidence
    if data.community_reports >= 2:
        confidence += 0.10
    elif data.community_reports == 1:
        confidence += 0.05

    # Keep it within a safe range
    confidence = max(0.0, min(confidence, 0.95))

    return round(confidence, 2)


def calculate_flood_risk(
    data: FloodRiskInput
) -> tuple[int, RiskLevel, list[str], float]:

    score = 0
    reasons: list[str] = []

    # -------------------------
    # 1. Short-term rainfall
    # -------------------------

    if data.rainfall_1h_mm >= 30:
        score += 30
        reasons.append("High short-term rainfall")

    elif data.rainfall_1h_mm >= 15:
        score += 18
        reasons.append("Elevated short-term rainfall")

    # -------------------------
    # 2. Accumulated rainfall
    # -------------------------

    if data.rainfall_24h_mm >= 80:
        score += 35
        reasons.append("High accumulated rainfall")

    elif data.rainfall_24h_mm >= 40:
        score += 20
        reasons.append("Elevated accumulated rainfall")

    # -------------------------
    # 3. Rainfall trend
    # -------------------------

    if data.previous_rainfall_24h_mm is not None:

        increase = (
            data.rainfall_24h_mm
            - data.previous_rainfall_24h_mm
        )

        if increase >= 20:
            score += 10
            reasons.append(
                "Accumulated rainfall is increasing significantly"
            )

        elif increase >= 10:
            score += 5
            reasons.append(
                "Accumulated rainfall is increasing"
            )

    # -------------------------
    # 4. Community evidence
    # -------------------------

    if data.community_reports >= 5:
        score += 20
        reasons.append(
            "Multiple community reports indicate flooding"
        )

    elif data.community_reports >= 2:
        score += 12
        reasons.append(
            "Community reports indicate possible flooding"
        )

    elif data.community_reports == 1:
        score += 5
        reasons.append(
            "A recent community report indicates possible flooding"
        )

    # Never exceed 100
    score = min(score, 100)

    # -------------------------
    # Risk classification
    # -------------------------

    if score >= 80:
        level: RiskLevel = "critical"

    elif score >= 60:
        level = "high"

    elif score >= 30:
        level = "moderate"

    else:
        level = "low"

    confidence = calculate_confidence(data)

    if not reasons:
        reasons.append(
            "No significant flood-risk indicators detected"
        )

    return score, level, reasons, confidence