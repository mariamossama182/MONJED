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
        +---- Voice (future)


IMPORTANT:
- Does NOT generate alerts.
- Does NOT modify decisions.
- Does NOT format messages.
- Only coordinates delivery.
"""


from AI.ai_alert.alert_formatter import (
    format_dashboard_alert,
)


from backend.app.services.sms.sms_service import (
    send_alert_sms,
)



# ============================================================
# DASHBOARD DELIVERY
# ============================================================


def prepare_dashboard_alert(
    alert: dict,
) -> dict:
    """
    Prepare alert for frontend dashboard.
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
    Send alert through SMS channel.

    SMS formatting is handled internally
    by SMS service layer.

    Dispatcher only coordinates delivery.
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


        result = send_alert_sms(

            phone,

            alert,

        )


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
# VOICE READY
# ============================================================


def prepare_voice_alert(
    alert: dict,
) -> None:
    """
    Future voice alert integration.

    Reserved for:
    - Text To Speech
    - Voice assistants
    - Accessibility channels

    Not implemented yet.
    """

    return None



# ============================================================
# FULL DISPATCH
# ============================================================


def dispatch_alert(
    alert: dict,
    sms_recipients: list[str] | None = None,
) -> dict:
    """
    Main MONJED alert delivery function.

    Sends alert to available channels.

    Input:
        Normalized MONJED alert.

    Output:
        Delivery status per channel.
    """



    result = {


        "dashboard":

            prepare_dashboard_alert(
                alert
            ),



        "sms":

            [],



        "voice":

            prepare_voice_alert(
                alert
            ),

    }



    if sms_recipients:


        result["sms"] = (

            send_sms_alert(

                alert,

                sms_recipients,

            )

        )



    return result