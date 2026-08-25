from risk_engine.earthquake import (
    get_earthquakes,
    parse_earthquakes,
    extract_earthquake_features
)
from risk_engine.flood import (
    get_rainfall_data,
    parse_rainfall_data,
    extract_flood_features
)
from risk_engine.scoring import (
    calculate_earthquake_score,
    calculate_flood_score,
    get_risk_level
)

COUNTRY = "Kenya"
START = "2026-07-21"
END = "2026-08-20"

print(f"================ Risk Assessment: {COUNTRY} ================\n")

# --- 1. Earthquake Pipeline ---
raw_eq = get_earthquakes(country=COUNTRY, start_time=START, end_time=END, min_magnitude=2.0)
cleaned_eq = parse_earthquakes(raw_eq)
eq_features = extract_earthquake_features(cleaned_eq)
eq_result = calculate_earthquake_score(eq_features)

print("--- Earthquake Analysis ---")
print(f"Features: {eq_features}")
print(f"Score: {eq_result['score']} / 100 ({get_risk_level(eq_result['score'])})")
print(f"Reasons: {eq_result['reasons']}\n")

# --- 2. Flood Pipeline ---
raw_rain = get_rainfall_data(country=COUNTRY, start_date=START, end_date=END)
cleaned_rain = parse_rainfall_data(raw_rain)
flood_features = extract_flood_features(cleaned_rain, recent_days=3)
flood_result = calculate_flood_score(flood_features)

print("--- Flood Analysis ---")
print(f"Features: {flood_features}")
print(f"Score: {flood_result['score']} / 100 ({get_risk_level(flood_result['score'])})")
print(f"Reasons: {flood_result['reasons']}")



import json
from risk_engine.engine import evaluate_country_risk
COUNTRY = "Kenya"

print(f"Running Monjed AI Risk Engine for {COUNTRY}...\n")
report = evaluate_country_risk(country=COUNTRY, days_window=30)

print(json.dumps(report, indent=2))