"""
MONJED SMS Service Layer

This layer is the only interface used by
MONJED backend logic to send SMS alerts.

Responsibilities:
- Validate SMS request.
- Format emergency alert message.
- Send message through selected provider.
- Return normalized delivery result.

Architecture:

MONJED Alert
      |
      ↓
SMS Service Layer
      |
      ↓
SMS Formatter
      |
      ↓
Africa's Talking Provider


Important:
- Does NOT calculate risk.
- Does NOT modify decisions.
- Provider can be replaced without touching MONJED logic.
"""


from backend.app.services.sms.africas_talking import (
    send_sms as send_provider_sms,
)


from backend.app.services.sms.sms_formatter import (
    format_sms_alert,
)



# ============================================================
# SEND ALERT SMS
# ============================================================


def send_alert_sms(
    phone_number: str,
    alert: dict,
) -> dict:
    """
    Send MONJED emergency alert SMS.

    Args:
        phone_number:
            Destination phone number.

        alert:
            Normalized MONJED alert object.

    Returns:
        Normalized delivery result.

    Example:

    {
        "success": True,
        "response": {...}
    }

    """


    # --------------------------------------------------------
    # Validate phone number
    # --------------------------------------------------------

    if not phone_number:

        return {

            "success": False,

            "error":
                "Phone number is required",

        }



    # --------------------------------------------------------
    # Validate alert payload
    # --------------------------------------------------------

    if not isinstance(
        alert,
        dict,
    ):

        return {

            "success": False,

            "error":
                "Alert payload must be a dictionary",

        }



    # --------------------------------------------------------
    # Generate human-readable SMS
    # --------------------------------------------------------

    try:

        message = format_sms_alert(
            alert
        )


    except Exception as error:

        return {

            "success": False,

            "error":
                f"SMS formatting failed: {error}",

        }



    if not message:

        return {

            "success": False,

            "error":
                "Generated SMS message is empty",

        }



    # --------------------------------------------------------
    # Send using provider
    # --------------------------------------------------------

    return send_provider_sms(

        phone_number,

        message,

    )