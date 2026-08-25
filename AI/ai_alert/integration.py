"""
MONJED AI - AI Integration Layer

This module is the bridge between:

Backend
    |
    ↓
AI Adapter
    |
    ↓
Risk Engine
    |
    ↓
Gemini Alert Generator
    |
    ↓
Validated AI Alert


Responsibilities:
-----------------
- Prepare safe AI input payload
- Run AI alert generation pipeline
- Return validated AI output


IMPORTANT:
-----------
- AI does NOT calculate final decisions.
- AI does NOT send messages.
- AI does NOT dispatch alerts.
- Backend remains the source of truth.
"""


import json
from datetime import datetime, timezone



# ============================================================
# IMPORTS
# ============================================================


from backend.app.services.ai_adapter import (
    build_ai_payload,
)


from AI.ai_alert.gemini_alert import (
    generate_alert,
)



# ============================================================
# CONSTANTS
# ============================================================


AI_SOURCE = "MONJED_AI_PIPELINE"



# ============================================================
# HELPERS
# ============================================================


def _safe_json_print(
    title: str,
    data: dict,
):
    """
    Safe debug printing.
    """

    print(
        f"\n========== {title} =========="
    )


    print(

        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    )



def _validate_input(
    assessment: dict,
):
    """
    Validate backend assessment payload.
    """

    if not isinstance(
        assessment,
        dict,
    ):

        raise TypeError(
            "assessment must be a dictionary."
        )


    if not assessment:

        raise ValueError(
            "assessment cannot be empty."
        )



# ============================================================
# MAIN AI PIPELINE
# ============================================================


def run_ai_pipeline(
    assessment: dict,
    accessibility: list | None = None,
    language: str = "en",
) -> dict:
    """
    Execute complete MONJED AI pipeline.


    Flow:

    Backend Assessment

            |
            ↓

    AI Adapter

            |
            ↓

    Gemini Alert Generator

            |
            ↓

    Validation

            |
            ↓

    AI Alert Response



    Returns:

    {
        "metadata": {},
        "payload": {},
        "alert": {}
    }


    """


    # --------------------------------------------------------
    # 0. Validate Input
    # --------------------------------------------------------

    _validate_input(
        assessment
    )



    start_time = datetime.now(
        timezone.utc
    )



    # --------------------------------------------------------
    # 1. Build Safe AI Payload
    # --------------------------------------------------------

    ai_payload = build_ai_payload(

        assessment=assessment,

        accessibility=accessibility,

        language=language,

    )



    _safe_json_print(

        "AI PAYLOAD",

        ai_payload,

    )



    # --------------------------------------------------------
    # 2. Generate AI Alert
    # --------------------------------------------------------

    ai_alert = generate_alert(

        ai_payload

    )



    if not isinstance(
        ai_alert,
        dict,
    ):

        raise RuntimeError(
            "AI alert generation failed."
        )



    _safe_json_print(

        "AI ALERT",

        ai_alert,

    )



    # --------------------------------------------------------
    # 3. Metadata
    # --------------------------------------------------------

    end_time = datetime.now(
        timezone.utc
    )


    metadata = {

        "source":
            AI_SOURCE,


        "started_at":
            start_time.isoformat(),


        "completed_at":
            end_time.isoformat(),


        "processing_time_ms":
            int(
                (
                    end_time - start_time
                ).total_seconds()
                *
                1000
            ),

    }



    # --------------------------------------------------------
    # 4. Return Unified AI Result
    # --------------------------------------------------------

    return {


        "metadata":

            metadata,


        "payload":

            ai_payload,


        "alert":

            ai_alert,

    }



# ============================================================
# LOCAL TEST
# ============================================================


if __name__ == "__main__":

    print(
        """
MONJED AI Integration Layer

This module should be called
from backend services or API endpoints.
"""
    )