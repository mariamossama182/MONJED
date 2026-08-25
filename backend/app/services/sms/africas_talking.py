"""
MONJED Africa's Talking SMS Provider

Low-level SMS communication layer.

Responsibilities:
- Communicate with Africa's Talking REST API.
- Return normalized responses.

This module contains NO MONJED business logic.
"""

import json
import urllib.parse
import urllib.request
import urllib.error


from backend.app.services.sms.config import (
    AFRICAS_TALKING_USERNAME,
    AFRICAS_TALKING_API_KEY,
    AFRICAS_TALKING_SENDER_ID,
)


# ============================================================
# CONFIG
# ============================================================

AFRICAS_TALKING_SMS_URL = (
    "https://api.sandbox.africastalking.com/version1/messaging"
)


# ============================================================
# SEND SMS
# ============================================================


def send_sms(
    phone_number: str,
    message: str,
) -> dict:
    """
    Send SMS using Africa's Talking API.

    Returns normalized MONJED response.
    """


    if not AFRICAS_TALKING_USERNAME:
        return {
            "success": False,
            "error": "Missing Africa's Talking username",
        }


    if not AFRICAS_TALKING_API_KEY:
        return {
            "success": False,
            "error": "Missing Africa's Talking API key",
        }


    if not phone_number:
        return {
            "success": False,
            "error": "Phone number is required",
        }


    if not message:
        return {
            "success": False,
            "error": "Message is empty",
        }



    payload = {

        "username":
            AFRICAS_TALKING_USERNAME,

        "to":
            phone_number,

        "message":
            message,

    }


    if AFRICAS_TALKING_SENDER_ID:

        payload["from"] = (
            AFRICAS_TALKING_SENDER_ID
        )


    encoded_data = urllib.parse.urlencode(
        payload
    ).encode(
        "utf-8"
    )


    request = urllib.request.Request(

        AFRICAS_TALKING_SMS_URL,

        data=encoded_data,

        headers={

            "apiKey":
                AFRICAS_TALKING_API_KEY,

            "Accept":
                "application/json",

            "Content-Type":
                "application/x-www-form-urlencoded",

        },

        method="POST",

    )


    try:

        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:


            body = response.read().decode(
                "utf-8"
            )


            return {

                "success":
                    response.status == 201,

                "status_code":
                    response.status,

                "response":
                    json.loads(body)
                    if body
                    else None,

            }



    except urllib.error.HTTPError as error:

        body = error.read().decode(
            "utf-8"
        )


        return {

            "success":
                False,

            "status_code":
                error.code,

            "error":
                body,

        }



    except Exception as error:

        return {

            "success":
                False,

            "error":
                str(error),

        }