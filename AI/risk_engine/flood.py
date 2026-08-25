"""
MONJED AI - Flood Data Engine

Responsibilities:
- Fetch rainfall data from NASA POWER
- Parse precipitation records
- Extract flood risk features

This module does NOT:
- calculate risk score
- make decisions
- generate alerts
"""


import requests



NASA_POWER_URL = (
    "https://power.larc.nasa.gov/"
    "api/temporal/daily/point"
)



# ============================================================
# AFRICA COUNTRY LOCATIONS
# Representative points for MVP coverage
#
# Future upgrade:
# country -> zones -> multiple coordinates
# ============================================================


COUNTRY_LOCATIONS = {


    # =========================
    # North Africa
    # =========================

    "Egypt": {
        "latitude": 26.8206,
        "longitude": 30.8025,
        "radius_km": 500,
    },


    "Morocco": {
        "latitude": 31.7917,
        "longitude": -7.0926,
        "radius_km": 500,
    },


    "Algeria": {
        "latitude": 28.0339,
        "longitude": 1.6596,
        "radius_km": 500,
    },



    # =========================
    # East Africa
    # =========================

    "Kenya": {
        "latitude": -0.0236,
        "longitude": 37.9062,
        "radius_km": 500,
    },


    "Ethiopia": {
        "latitude": 9.1450,
        "longitude": 40.4897,
        "radius_km": 500,
    },


    "Tanzania": {
        "latitude": -6.3690,
        "longitude": 34.8888,
        "radius_km": 500,
    },


    "Uganda": {
        "latitude": 1.3733,
        "longitude": 32.2903,
        "radius_km": 500,
    },



    # =========================
    # Nile / Horn Region
    # =========================

    "Sudan": {
        "latitude": 12.8628,
        "longitude": 30.2176,
        "radius_km": 500,
    },



    # =========================
    # West Africa
    # =========================

    "Nigeria": {
        "latitude": 9.0820,
        "longitude": 8.6753,
        "radius_km": 500,
    },


    "Ghana": {
        "latitude": 7.9465,
        "longitude": -1.0232,
        "radius_km": 500,
    },



    # =========================
    # Southern Africa
    # =========================

    "South Africa": {
        "latitude": -30.5595,
        "longitude": 22.9375,
        "radius_km": 500,
    },


    "Mozambique": {
        "latitude": -18.6657,
        "longitude": 35.5296,
        "radius_km": 500,
    },

}



# ============================================================
# FETCH RAINFALL
# ============================================================


def get_rainfall_data(
    country,
    start_date,
    end_date,
):
    """
    Fetch daily rainfall from NASA POWER.
    """


    if country not in COUNTRY_LOCATIONS:

        raise ValueError(
            f"Country '{country}' is not configured."
        )



    location = COUNTRY_LOCATIONS[country]



    params = {


        "parameters":
            "PRECTOTCORR",


        "community":
            "RE",


        "longitude":
            location["longitude"],


        "latitude":
            location["latitude"],


        "start":
            start_date.replace(
                "-",
                ""
            ),


        "end":
            end_date.replace(
                "-",
                ""
            ),


        "format":
            "JSON",

    }



    try:

        response = requests.get(

            NASA_POWER_URL,

            params=params,

            timeout=30,

        )


        response.raise_for_status()


        return response.json()



    except requests.RequestException:


        return {}



# ============================================================
# PARSE DATA
# ============================================================


def parse_rainfall_data(
    raw_data,
):
    """
    Extract clean rainfall values.
    """


    try:


        parameters = (

            raw_data

            .get(
                "properties",
                {}
            )

            .get(
                "parameter",
                {}
            )

        )



        rainfall = parameters.get(
            "PRECTOTCORR",
            {}
        )



        return {


            date:
                value


            for date, value in rainfall.items()


            if isinstance(
                value,
                (int,float)
            )

            and value >= 0

        }



    except Exception:


        return {}



# ============================================================
# FEATURE EXTRACTION
# ============================================================


def extract_flood_features(
    rainfall_data,
    recent_days=3,
):
    """
    Extract flood features:

    - Average daily rainfall
    - Recent rainfall
    - Cumulative rainfall
    """



    if not rainfall_data:


        return {


            "average_daily_rainfall":
                0.0,


            "recent_daily_rainfall":
                0.0,


            "cumulative_rainfall":
                0.0,


            "days_analyzed":
                0,

        }




    dates = sorted(
        rainfall_data.keys()
    )



    values = [

        rainfall_data[date]

        for date in dates

    ]



    total = sum(
        values
    )


    days = len(
        values
    )



    average_daily = (

        total / days

        if days

        else 0

    )



    recent_values = values[-recent_days:]



    recent_average = (

        sum(recent_values)

        /

        len(recent_values)

        if recent_values

        else 0

    )



    return {


        "average_daily_rainfall":
            round(
                average_daily,
                2
            ),


        "recent_daily_rainfall":
            round(
                recent_average,
                2
            ),


        "cumulative_rainfall":
            round(
                total,
                2
            ),


        "days_analyzed":
            days,

    }