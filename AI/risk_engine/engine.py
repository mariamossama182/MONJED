"""
MONJED AI Risk Engine Orchestrator

Responsible for:
- Collecting hazard data
- Extracting features
- Generating standardized Risk Assessment

Does NOT:
- make decisions
- generate alerts
"""


from datetime import (
    datetime,
    timedelta,
    timezone,
)


from risk_engine.earthquake import (
    get_earthquakes,
    parse_earthquakes,
    extract_earthquake_features,
)


from risk_engine.flood import (
    get_rainfall_data,
    parse_rainfall_data,
    extract_flood_features,
)


from risk_engine.scoring import (
    calculate_earthquake_score,
    calculate_flood_score,
)



# ============================================================
# EARTHQUAKE ASSESSMENT
# ============================================================


def evaluate_earthquake_risk(
    country: str,
    days_window: int = 30,
):


    now = datetime.now(
        timezone.utc
    )


    start = now - timedelta(
        days=days_window
    )



    raw = get_earthquakes(
        country=country,
        start_time=start.strftime("%Y-%m-%d"),
        end_time=now.strftime("%Y-%m-%d"),
        min_magnitude=2.0,
    )


    cleaned = parse_earthquakes(
        raw
    )


    features = extract_earthquake_features(
        cleaned,
        recent_days=7,
    )


    assessment = calculate_earthquake_score(
        features
    )



    return {

        "hazard":
            "earthquake",


        "country":
            country,


        "risk_score":
            assessment["score"],


        "risk_level":
            assessment["risk_level"],


        "confidence":
            assessment["confidence"],


        "reasons":
            assessment["reasons"],


        "features":
            features,


        "evaluated_at":
            now.isoformat(),

    }




# ============================================================
# FLOOD ASSESSMENT
# ============================================================


def evaluate_flood_risk(
    country: str,
    days_window: int = 30,
):


    now = datetime.now(
        timezone.utc
    )


    start = now - timedelta(
        days=days_window
    )



    raw = get_rainfall_data(
        country=country,
        start_date=start.strftime("%Y-%m-%d"),
        end_date=now.strftime("%Y-%m-%d"),
    )



    cleaned = parse_rainfall_data(
        raw
    )


    features = extract_flood_features(
        cleaned,
        recent_days=3,
    )



    assessment = calculate_flood_score(
        features
    )



    return {

        "hazard":
            "flood",


        "country":
            country,


        "risk_score":
            assessment["score"],


        "risk_level":
            assessment["risk_level"],


        "confidence":
            assessment["confidence"],


        "reasons":
            assessment["reasons"],


        "features":
            features,


        "evaluated_at":
            now.isoformat(),

    }