"""
MONJED AI - Alert Dispatcher

Responsible only for delivering validated alerts
through available communication channels.

Architecture:

Normalized Alert
        |
        |
        +---- Dashboard
        |
        +---- SMS
        |
        +---- Voice


IMPORTANT:
- Does NOT generate alerts.
- Does NOT calculate risk.
- Does NOT modify decisions.
- Does NOT make safety decisions.
- Only coordinates delivery.
"""


from AI.ai_alert.alert_formatter import (
    format_dashboard_alert,
)


from backend.app.services.sms.sms_service import (
    send_alert_sms,
)


from backend.app.services.voice.voice_service import (
    send_voice_alert,
)



# ============================================================
# VALIDATION
# ============================================================


def _validate_alert(
    alert: dict,
):

    if not isinstance(
        alert,
        dict,
    ):

        raise TypeError(
            "alert must be a dictionary."
        )


    if not alert:

        raise ValueError(
            "alert cannot be empty."
        )



# ============================================================
# NOTIFICATION CHECK
# ============================================================


def _notification_allowed(
    alert: dict,
) -> bool:
    """
    Check whether active notification
    channels are allowed.

    Decision Engine is the source
    of this information.
    """


    return bool(

        alert.get(

            "notification_required",

            False,

        )

    )



# ============================================================
# DASHBOARD DELIVERY
# ============================================================


def prepare_dashboard_alert(
    alert: dict,
) -> dict:
    """
    Dashboard always receives updates.

    Monitoring states are displayed
    even when notification is disabled.
    """


    return format_dashboard_alert(
        alert
    )



# ============================================================
# SMS DELIVERY
# ============================================================


def send_sms_alert(
    alert: dict,
    phone_numbers: list[str],
) -> list[dict]:
    """
    Send emergency SMS alerts.

    Dispatcher only coordinates.
    SMS service handles formatting.
    """


    if not isinstance(
        phone_numbers,
        list,
    ):

        raise TypeError(
            "phone_numbers must be a list."
        )


    results = []


    for phone in phone_numbers:


        try:

            result = send_alert_sms(

                phone,

                alert,

            )


        except Exception as error:


            result = {

                "success": False,

                "error":
                    str(error),

            }



        results.append(

            {

                "phone":
                    phone,


                "result":
                    result,

            }

        )


    return results



# ============================================================
# VOICE DELIVERY
# ============================================================


def prepare_voice_alert(
    alert: dict,
) -> dict:
    """
    Generate voice alert.

    Voice provider is isolated
    inside voice service layer.
    """


    return send_voice_alert(
        alert
    )



# ============================================================
# FULL DISPATCH
# ============================================================


def dispatch_alert(
    alert: dict,
    sms_recipients: list[str] | None = None,
) -> dict:
    """
    Main MONJED delivery coordinator.


    Behavior:

    notification_required = False

        Dashboard only


    notification_required = True

        Dashboard
        SMS
        Voice

    """


    _validate_alert(
        alert
    )



    result = {


        "dashboard":

            prepare_dashboard_alert(
                alert
            ),



        "sms":

            [],



        "voice":

            None,



        "notification_required":

            _notification_allowed(
                alert
            ),

    }



    # ========================================================
    # Emergency Channels
    # ========================================================


    if not _notification_allowed(
        alert
    ):


        result["voice"] = {

            "success":
                False,

            "message":
                "Notification not required. Dashboard update only.",

        }


        return result



    # ========================================================
    # SMS
    # ========================================================


    if sms_recipients:


        result["sms"] = send_sms_alert(

            alert,

            sms_recipients,

        )



    # ========================================================
    # Voice
    # ========================================================


    try:


        result["voice"] = prepare_voice_alert(

            alert

        )


    except Exception as error:


        result["voice"] = {

            "success":
                False,

            "error":
                str(error),

        }



    return result