"""
MONJED SMS Formatter

Converts normalized alerts into
human-readable emergency SMS.

Rules:
- No decision making.
- No risk calculation.
- Uses backend-approved actions.
"""


SUPPORTED_LANGUAGES = {

    "en",
    "sw",
    "ar",
    "fr",

}



# ============================================================
# TRANSLATIONS
# ============================================================


TRANSLATIONS = {


    "title":

    {

        "en": "MONJED ALERT",
        "sw": "TAHADHARI YA MONJED",
        "ar": "تنبيه MONJED",
        "fr": "ALERTE MONJED",

    },


    "risk":

    {

        "en": "Risk",
        "sw": "Hatari",
        "ar": "الخطر",
        "fr": "Risque",

    },


    "action":

    {

        "en": "Action",
        "sw": "Hatua",
        "ar": "الإجراء",
        "fr": "Action",

    },


    "advice":

    {

        "en": "Safety advice",
        "sw": "Tahadhari",
        "ar": "نصيحة أمان",
        "fr": "Conseil",

    },


}



def _t(
    key,
    language
):

    return TRANSLATIONS[key].get(
        language,
        TRANSLATIONS[key]["en"]
    )



# ============================================================
# ACCESSIBILITY
# ============================================================


def _accessibility_lines(
    alert,
    language
):

    result = []


    needs = alert.get(
        "accessibility_needs",
        []
    )


    if "mobility" in needs:

        result.append(
            "Support needed: Assist people with mobility difficulties."
        )


    if "visual" in needs:

        result.append(
            "Use voice assistance when possible."
        )


    if "hearing" in needs:

        result.append(
            "Use visual notifications."
        )


    if "cognitive" in needs:

        result.append(
            "Provide simple step-by-step guidance."
        )


    return result



# ============================================================
# FORMATTER
# ============================================================


def format_sms_alert(
    alert: dict
):


    if not isinstance(
        alert,
        dict
    ):

        return ""



    language = alert.get(
        "language",
        "en"
    )


    if language not in SUPPORTED_LANGUAGES:

        language = "en"



    lines = []



    lines.append(
        _t(
            "title",
            language
        )
    )



    country = alert.get(
        "country"
    )


    if country:

        lines.append(
            country
        )



    hazards = alert.get(
        "hazards",
        []
    )


    if hazards:

        hazard = hazards[0]


        lines.append(
            f"{hazard.get('type','HAZARD').upper()} "
            f"({_t('risk',language)}: "
            f"{hazard.get('risk_level','unknown')})"
        )



    decision = alert.get(
        "final_decision",
        {}
    )



    action = decision.get(
        "current_action"
    )


    if action:

        lines.append(
            f"{_t('action',language)}: {action}"
        )



    backup = decision.get(
        "backup_action"
    )


    if backup:

        lines.append(
            f"{_t('advice',language)}: {backup}"
        )



    lines.extend(
        _accessibility_lines(
            alert,
            language
        )
    )



    return "\n".join(
        lines
    )