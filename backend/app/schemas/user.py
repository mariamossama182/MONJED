from typing import Literal

from pydantic import BaseModel, Field


SupportedLanguage = Literal[
    "en",
    "ar",
    "sw",
    "fr",
]


AccessibilityNeed = Literal[
    "mobility",
    "visual",
    "hearing",
    "cognitive",
]


class UserProfileResponse(BaseModel):

    user_id: str

    display_name: str | None = None

    role: str | None = None

    zone_id: str | None = None

    preferred_language: str = "en"

    accessibility_needs: list[str] = Field(
        default_factory=list
    )

    notification_consent: bool = False


class UserProfileUpdate(BaseModel):

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    zone_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    preferred_language: SupportedLanguage | None = None

    accessibility_needs: list[AccessibilityNeed] | None = None

    notification_consent: bool | None = None
