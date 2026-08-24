"""
Monjed AI - Gemini Alert Layer

Production Architecture:

Risk Engine
      ↓
Decision Engine
      ↓
Accessibility Layer
      ↓
AI Adapter
      ↓
Gemini Alert Layer
      ↓
Validation
      ↓
Dashboard / SMS


IMPORTANT:
- Gemini is a communication layer only.
- Gemini does NOT calculate risk.
- Gemini does NOT make decisions.
- Gemini does NOT receive raw environmental data.
- The backend payload is the source of truth.
- Gemini cannot modify safety-critical backend values.
- If Gemini is unavailable or returns invalid output,
  a deterministic fallback alert is returned.
"""


import json
import os
import time

from datetime import datetime, timezone

from dotenv import load_dotenv

from google import genai
from google.genai import types


# ============================================================
# CONSTANTS
# ============================================================

SUPPORTED_LANGUAGES = [
    "en",
    "ar",
    "fr",
    "sw",
]


VALID_DECISION_STATUSES = [
    "no_adjustment",
    "action_adjusted",
    "human_review_required",
]


# ============================================================
# 1. ENVIRONMENT
# ============================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


# ============================================================
# 2. GEMINI CLIENT
#
# MONJED must continue operating if Gemini is unavailable.
# ============================================================

client = None


if GEMINI_API_KEY:

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    except Exception as error:

        print(
            "Gemini client initialization failed. "
            "Deterministic fallback mode will be used."
        )

        print(
            f"Client error: {error}"
        )


# ============================================================
# 3. HELPERS
# ============================================================

def _utc_timestamp() -> str:
    """
    Return the current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()

def _is_non_retryable_gemini_error(
    error: Exception,
) -> bool:
    """
    Detect Gemini errors where retrying the same request
    immediately is unlikely to help.

    MONJED prefers the deterministic fallback over adding
    unnecessary latency in safety-related communication.

    This intentionally avoids depending on one specific
    google-genai exception class so it remains resilient
    across SDK versions.
    """

    message = str(
        error
    ).lower()

    non_retryable_indicators = (
        # Quota / rate limit
        "429",
        "resource_exhausted",
        "quota exceeded",
        "too_many_requests",
        "rate limit",
        "rate-limit",

        # Authentication / authorization
        "401",
        "unauthenticated",
        "invalid api key",
        "api key not valid",

        "403",
        "permission_denied",
        "permission denied",

        # Invalid request / unsupported model
        "400",
        "invalid_argument",
        "invalid argument",

        "404",
        "not_found",
        "model not found",
    )

    return any(
        indicator in message
        for indicator in non_retryable_indicators
    )

def _get_hazards(
    payload: dict,
) -> list:
    """
    Return normalized hazards from the AI Adapter payload.
    """

    hazards = payload.get(
        "hazards",
        []
    )

    if not isinstance(
        hazards,
        list,
    ):
        return []

    return hazards


def _get_decision(
    payload: dict,
) -> dict:
    """
    Return the deterministic backend decision.

    IMPORTANT:
    The AI Adapter exposes the protected decision
    through the key "decision".
    """

    decision = payload.get(
        "decision",
        {}
    )

    if not isinstance(
        decision,
        dict,
    ):
        return {}

    return decision


def _get_accessibility_needs(
    payload: dict,
) -> list:
    """
    Safely return accessibility needs.
    """

    needs = payload.get(
        "accessibility_needs",
        []
    )

    if not isinstance(
        needs,
        list,
    ):
        return []

    return needs


def _build_community_summary(
    payload: dict,
) -> str:
    """
    Build a deterministic community-evidence summary.

    IMPORTANT:
    - This does NOT claim community reports are verified.
    - The count represents evidence items considered by
      the Decision Engine.
    - Community evidence does NOT represent scientific
      hazard measurements.
    """

    evidence = payload.get(
        "community_evidence",
        {}
    )

    if not isinstance(
        evidence,
        dict,
    ):
        return (
            "No recent community evidence items were used "
            "in the operational decision."
        )

    evidence_items = evidence.get(
        "matching_reports",
        0
    )

    if not isinstance(
        evidence_items,
        int,
    ):
        evidence_items = 0

    evidence_items = max(
        0,
        evidence_items,
    )

    if evidence_items == 1:
        return (
            "1 recent community evidence item was considered "
            "in the operational decision."
        )

    if evidence_items > 1:
        return (
            f"{evidence_items} recent community evidence items "
            "were considered in the operational decision."
        )

    return (
        "No recent community evidence items were used "
        "in the operational decision."
    )

# ============================================================
# 4. DETERMINISTIC FALLBACK ALERT
# ============================================================

def build_fallback_alert(
    payload: dict,
) -> dict:
    """
    Build a deterministic alert when Gemini is unavailable
    or its output fails validation.

    Every safety-critical value comes directly from
    the backend-approved AI payload.
    """

    zone_id = payload.get(
        "zone_id",
        "UNKNOWN"
    )

    country = payload.get(
        "country",
        "UNKNOWN"
    )

    language = payload.get(
        "language",
        "en"
    )

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    hazards = _get_hazards(
        payload
    )

    decision = _get_decision(
        payload
    )

    accessibility_needs = (
        _get_accessibility_needs(
            payload
        )
    )

    decision_status = decision.get(
        "decision_status",
        "no_adjustment"
    )

    if (
        decision_status
        not in VALID_DECISION_STATUSES
    ):
        decision_status = "no_adjustment"

    current_action = decision.get(
        "current_action",
        "Follow official safety guidance."
    )

    backup_action = decision.get(
        "backup_action",
        "Follow local authority instructions if conditions change."
    )

    accessibility_instructions = (
        decision.get(
            "accessibility_instructions",
            []
        )
    )

    if not isinstance(
        accessibility_instructions,
        list,
    ):
        accessibility_instructions = []

    community_summary = (
        _build_community_summary(
            payload
        )
    )

    formatted_hazards = []

    for hazard in hazards:

        if not isinstance(
            hazard,
            dict,
        ):
            continue

        hazard_type = hazard.get(
            "hazard",
            "UNKNOWN"
        )

        risk_score = hazard.get(
            "risk_score"
        )

        risk_level = hazard.get(
            "risk_level"
        )

        hazard_reasons = hazard.get(
            "reasons",
            []
        )

        if (
            isinstance(
                hazard_reasons,
                list,
            )
            and hazard_reasons
        ):

            message = str(
                hazard_reasons[0]
            )

        else:

            message = (
                f"{hazard_type} risk is currently "
                "being monitored."
            )

        formatted_hazards.append(
            {
                "type":
                    hazard_type,

                "risk_score":
                    risk_score,

                "risk_level":
                    risk_level,

                "message":
                    message,
            }
        )

    alert_message = (
        f"Zone {zone_id} in {country}. "
        f"Current action: {current_action} "
        f"Backup action: {backup_action}"
    )

    if accessibility_instructions:

        alert_message += (
            " Accessibility support instructions "
            "are included in the alert details."
        )

    return {

        "title":
            f"MONJED Alert - Zone {zone_id}",

        "zone_id":
            zone_id,

        "country":
            country,

        "language":
            language,

        "hazards":
            formatted_hazards,

        "community_evidence_summary":
            community_summary,

        "final_decision": {

            "decision_status":
                decision_status,

            "current_action":
                current_action,

            "backup_action":
                backup_action,

            "accessibility_instructions":
                accessibility_instructions,
        },

        "accessibility_needs":
            accessibility_needs,

        "alert_message":
            alert_message,

        "alert_source":
            "DETERMINISTIC_FALLBACK",

        "generated_by":
            "DETERMINISTIC_FALLBACK",

        "generated_at":
            _utc_timestamp(),

        "confidence_source":
            "backend",
    }


# ============================================================
# 5. AI OUTPUT VALIDATION
# ============================================================

def validate_ai_alert(
    payload: dict,
    alert: dict,
) -> dict:
    """
    Validate Gemini output against the protected backend payload.

    Gemini MUST NOT modify:

    - zone_id
    - country
    - language
    - hazard identity
    - risk_score
    - risk_level
    - decision_status
    - current_action
    - backup_action
    - accessibility_instructions
    - accessibility_needs
    - community evidence summary
    """

    errors = []


    if not isinstance(
        alert,
        dict,
    ):

        return {
            "valid": False,
            "errors": [
                "AI output must be a dictionary."
            ],
        }


    # ========================================================
    # ZONE
    # ========================================================

    if alert.get(
        "zone_id"
    ) != payload.get(
        "zone_id"
    ):

        errors.append(
            "zone_id was modified by AI."
        )


    # ========================================================
    # COUNTRY
    # ========================================================

    if alert.get(
        "country"
    ) != payload.get(
        "country"
    ):

        errors.append(
            "country was modified by AI."
        )


    # ========================================================
    # LANGUAGE
    # ========================================================

    actual_language = alert.get(
        "language"
    )

    expected_language = payload.get(
        "language"
    )

    if (
        actual_language
        not in SUPPORTED_LANGUAGES
    ):

        errors.append(
            "Unsupported language."
        )

    if (
        actual_language
        != expected_language
    ):

        errors.append(
            "language was modified by AI."
        )


    # ========================================================
    # HAZARDS
    # ========================================================

    expected_hazards = _get_hazards(
        payload
    )

    actual_hazards = alert.get(
        "hazards",
        []
    )

    if not isinstance(
        actual_hazards,
        list,
    ):

        errors.append(
            "hazards must be a list."
        )

    elif len(
        actual_hazards
    ) != len(
        expected_hazards
    ):

        errors.append(
            "hazard count was modified by AI."
        )

    else:

        for index, expected in enumerate(
            expected_hazards
        ):

            actual = actual_hazards[
                index
            ]

            if not isinstance(
                actual,
                dict,
            ):

                errors.append(
                    f"Hazard at index {index} "
                    "is not a dictionary."
                )

                continue

            expected_type = expected.get(
                "hazard"
            )

            actual_type = actual.get(
                "type"
            )

            if (
                actual_type
                != expected_type
            ):

                errors.append(
                    f"Hazard mismatch at index "
                    f"{index}: expected "
                    f"{expected_type}, got "
                    f"{actual_type}."
                )

            if (
                actual.get(
                    "risk_score"
                )
                != expected.get(
                    "risk_score"
                )
            ):

                errors.append(
                    f"{expected_type} risk_score "
                    "was modified by AI."
                )

            if (
                actual.get(
                    "risk_level"
                )
                != expected.get(
                    "risk_level"
                )
            ):

                errors.append(
                    f"{expected_type} risk_level "
                    "was modified by AI."
                )


    # ========================================================
    # DECISION
    # ========================================================

    expected_decision = (
        _get_decision(
            payload
        )
    )

    actual_decision = alert.get(
        "final_decision",
        {}
    )

    if not isinstance(
        actual_decision,
        dict,
    ):

        errors.append(
            "final_decision must be a dictionary."
        )

    else:

        protected_fields = [
            "decision_status",
            "current_action",
            "backup_action",
            "accessibility_instructions",
        ]

        for field in protected_fields:

            default_value = (
                []
                if field
                == "accessibility_instructions"
                else None
            )

            expected_value = (
                expected_decision.get(
                    field,
                    default_value,
                )
            )

            actual_value = (
                actual_decision.get(
                    field,
                    default_value,
                )
            )

            if (
                actual_value
                != expected_value
            ):

                errors.append(
                    f"{field} was modified by AI."
                )


    # ========================================================
    # DECISION STATUS SAFETY
    # ========================================================

    decision_status = (
        actual_decision.get(
            "decision_status"
        )
        if isinstance(
            actual_decision,
            dict,
        )
        else None
    )

    if (
        decision_status
        not in VALID_DECISION_STATUSES
    ):

        errors.append(
            "Invalid decision_status."
        )


    # ========================================================
    # ACCESSIBILITY NEEDS
    # ========================================================

    expected_needs = (
        _get_accessibility_needs(
            payload
        )
    )

    actual_needs = alert.get(
        "accessibility_needs",
        []
    )

    if (
        actual_needs
        != expected_needs
    ):

        errors.append(
            "accessibility_needs was modified by AI."
        )


    # ========================================================
    # COMMUNITY EVIDENCE SUMMARY
    # ========================================================

    expected_community_summary = (
        _build_community_summary(
            payload
        )
    )

    actual_community_summary = (
        alert.get(
            "community_evidence_summary"
        )
    )

    if (
        actual_community_summary
        != expected_community_summary
    ):

        errors.append(
            "community_evidence_summary was modified by AI."
        )


    # ========================================================
    # RESULT
    # ========================================================

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,
    }


# ============================================================
# 6. GENERATE AI ALERT
# ============================================================

def generate_alert(
    payload: dict,
) -> dict:
    """
    Generate a human-readable alert from an AI-ready payload.

    The payload must be created by ai_adapter.py.

    Gemini only improves communication and wording.
    The deterministic backend remains the source of truth.
    """

    # ========================================================
    # BASIC PAYLOAD VALIDATION
    # ========================================================

    if not isinstance(
        payload,
        dict,
    ):

        raise TypeError(
            "payload must be a dictionary."
        )


    required_fields = [
        "zone_id",
        "country",
        "language",
        "hazards",
        "decision",
    ]


    for field in required_fields:

        if field not in payload:

            raise ValueError(
                f"AI payload is missing required field: "
                f"{field}"
            )


    # ========================================================
    # LANGUAGE VALIDATION
    # ========================================================

    language = payload.get(
        "language"
    )

    if (
        language
        not in SUPPORTED_LANGUAGES
    ):

        raise ValueError(
            f"Unsupported AI payload language: {language}"
        )


    # ========================================================
    # HAZARD VALIDATION
    # ========================================================

    hazards = payload.get(
        "hazards"
    )

    if not isinstance(
        hazards,
        list,
    ):

        raise TypeError(
            "payload.hazards must be a list."
        )

    if not hazards:

        raise ValueError(
            "payload.hazards cannot be empty."
        )


    # ========================================================
    # DECISION VALIDATION
    # ========================================================

    decision = payload.get(
        "decision"
    )

    if not isinstance(
        decision,
        dict,
    ):

        raise TypeError(
            "payload.decision must be a dictionary."
        )


    decision_status = decision.get(
        "decision_status"
    )

    if (
        decision_status
        not in VALID_DECISION_STATUSES
    ):

        raise ValueError(
            f"Unsupported decision_status: "
            f"{decision_status}"
        )


    # ========================================================
    # GEMINI UNAVAILABLE
    # ========================================================

    if client is None:

        print(
            "Gemini client is unavailable. "
            "Using deterministic fallback alert."
        )

        return build_fallback_alert(
            payload
        )


    # ========================================================
    # PREPARE SAFE PROMPT PAYLOAD
    # ========================================================

    prompt_payload = dict(
        payload
    )

    prompt_payload[
        "community_evidence_summary"
    ] = _build_community_summary(
        payload
    )


    payload_json = json.dumps(
        prompt_payload,
        indent=2,
        ensure_ascii=False,
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are the communication layer of MONJED,
a safety-focused disaster early-warning and
action-support system.

Your ONLY responsibility is to transform the
backend-approved payload into a clear, concise,
human-readable alert.

THE BACKEND DECISION IS THE SOURCE OF TRUTH.

You MUST NOT:

- calculate or recalculate risk
- change any risk_score
- change any risk_level
- change, remove, reorder, or invent hazards
- change decision_status
- change current_action
- change backup_action
- change accessibility_instructions
- change accessibility_needs
- change community_evidence_summary
- create new emergency actions
- invent facts
- invent environmental conditions
- invent community reports
- claim evidence is verified unless explicitly stated
- add recommendations that are not present in the payload

You MAY ONLY:

- improve clarity
- simplify communication
- organize the alert for human readability
- write hazard messages based only on supplied reasons
- write a concise alert_message using only backend-approved actions
- preserve accessibility instructions exactly as provided

Protected fields MUST be copied exactly:

- zone_id
- country
- language
- hazard type
- risk_score
- risk_level
- decision_status
- current_action
- backup_action
- accessibility_instructions
- accessibility_needs
- community_evidence_summary

Generate human-readable text using the requested language:

en = English
ar = Arabic
fr = French
sw = Swahili

The backend language field MUST be followed when
writing the title, hazard message, and alert_message.

Do not translate or rewrite protected action fields.
They must remain exactly as supplied by the backend.

Return ONLY valid JSON matching the requested schema.

BACKEND AI PAYLOAD:

{payload_json}
"""


    # ========================================================
    # STRUCTURED OUTPUT SCHEMA
    # ========================================================

    alert_schema = {

        "type":
            "object",

        "properties": {

            "title": {
                "type":
                    "string"
            },

            "zone_id": {
                "type":
                    "string"
            },

            "country": {
                "type":
                    "string"
            },

            "language": {

                "type":
                    "string",

                "enum": [
                    "en",
                    "ar",
                    "fr",
                    "sw",
                ],
            },

            "hazards": {

                "type":
                    "array",

                "items": {

                    "type":
                        "object",

                    "properties": {

                        "type": {
                            "type":
                                "string"
                        },

                        "risk_score": {
                            "type":
                                "number"
                        },

                        "risk_level": {

                            "type":
                                "string",

                            "enum": [
                                "low",
                                "moderate",
                                "high",
                                "critical",
                            ],
                        },

                        "message": {
                            "type":
                                "string"
                        },
                    },

                    "required": [
                        "type",
                        "risk_score",
                        "risk_level",
                        "message",
                    ],
                },
            },

            "community_evidence_summary": {
                "type":
                    "string"
            },

            "final_decision": {

                "type":
                    "object",

                "properties": {

                    "decision_status": {

                        "type":
                            "string",

                        "enum": [
                            "no_adjustment",
                            "action_adjusted",
                            "human_review_required",
                        ],
                    },

                    "current_action": {
                        "type":
                            "string"
                    },

                    "backup_action": {
                        "type":
                            "string"
                    },

                    "accessibility_instructions": {

                        "type":
                            "array",

                        "items": {
                            "type":
                                "string"
                        },
                    },
                },

                "required": [
                    "decision_status",
                    "current_action",
                    "backup_action",
                    "accessibility_instructions",
                ],
            },

            "accessibility_needs": {

                "type":
                    "array",

                "items": {
                    "type":
                        "string"
                },
            },

            "alert_message": {

                "type":
                    "string",

                "maxLength":
                    300,
            },
        },

        "required": [
            "title",
            "zone_id",
            "country",
            "language",
            "hazards",
            "community_evidence_summary",
            "final_decision",
            "accessibility_needs",
            "alert_message",
        ],
    }


    # ========================================================
    # GEMINI CONFIGURATION
    # ========================================================

    config = types.GenerateContentConfig(

        temperature=0.2,

        response_mime_type=
            "application/json",

        response_schema=
            alert_schema,
    )


        # ========================================================
    # GEMINI RETRY
    #
    # Retry only errors that may reasonably be transient.
    #
    # Quota, authentication, authorization, configuration,
    # and invalid-request errors fall back immediately.
    # ========================================================

    max_attempts = 3

    response = None

    last_error = None


    for attempt in range(
        max_attempts
    ):

        try:

            chat = client.chats.create(
                model=GEMINI_MODEL,
                config=config,
            )

            response = chat.send_message(
                prompt
            )

            break

        except Exception as error:

            last_error = error

            # ------------------------------------------------
            # NON-RETRYABLE ERROR
            #
            # For quota/config/auth errors, waiting and sending
            # the same request again adds latency without making
            # MONJED safer.
            #
            # Use the deterministic backend alert immediately.
            # ------------------------------------------------

            if _is_non_retryable_gemini_error(
                error
            ):

                print(
                    "Gemini request failed with a "
                    "non-retryable error. "
                    "Using deterministic fallback immediately."
                )

                print(
                    f"Gemini error: {error}"
                )

                break

            # ------------------------------------------------
            # TRANSIENT ERROR
            # ------------------------------------------------

            attempts_remaining = (
                max_attempts
                - attempt
                - 1
            )

            if attempts_remaining > 0:

                # Short bounded backoff.
                # 2 seconds after attempt 1,
                # 4 seconds after attempt 2.
                wait_time = (
                    2
                    * (
                        attempt + 1
                    )
                )

                print(
                    "Gemini request temporarily failed. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

            else:

                print(
                    "Gemini unavailable after "
                    f"{max_attempts} attempts."
                )

                print(
                    f"Last error: {last_error}"
                )

                
    if response is None:

        print(
            "Using deterministic fallback alert."
        )

        return build_fallback_alert(
            payload
        )


    # ========================================================
    # PARSE GEMINI RESPONSE
    # ========================================================

    try:

        response_text = (
            response.text
        )

        alert = json.loads(
            response_text
        )

    except Exception as error:

        print(
            "Gemini response parsing failed. "
            "Using deterministic fallback alert."
        )

        print(
            f"Parsing error: {error}"
        )

        return build_fallback_alert(
            payload
        )


    # ========================================================
    # VALIDATE GEMINI OUTPUT
    # ========================================================

    validation = validate_ai_alert(
        payload,
        alert,
    )


    if not validation[
        "valid"
    ]:

        print(
            "Gemini output validation failed. "
            "Using deterministic fallback alert."
        )

        for error in validation[
            "errors"
        ]:

            print(
                f"- {error}"
            )

        return build_fallback_alert(
            payload
        )


    # ========================================================
    # ADD TRUSTED METADATA
    #
    # Metadata is added only after Gemini output passes
    # backend validation.
    # ========================================================

    alert[
        "alert_source"
    ] = "GEMINI"

    alert[
        "generated_by"
    ] = "GEMINI"

    alert[
        "generated_at"
    ] = _utc_timestamp()

    alert[
        "confidence_source"
    ] = "backend"


    # ========================================================
    # RETURN VALIDATED ALERT
    # ========================================================

    return alert