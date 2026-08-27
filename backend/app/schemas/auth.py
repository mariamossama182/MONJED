from typing import Literal

from pydantic import BaseModel, Field


RegisterRole = Literal[
    "citizen",
    "volunteer",
]


class RegisterRequest(BaseModel):

    display_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    role: RegisterRole = "citizen"

    zone_id: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    preferred_language: Literal[
        "en",
        "ar",
        "sw",
        "fr",
    ] = "en"

    accessibility_needs: list[str] = Field(
        default_factory=list
    )

    notification_consent: bool = False


class LoginRequest(BaseModel):

    # Email or international phone number.
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=254,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


class AuthUserResponse(BaseModel):

    user_id: str

    display_name: str | None = None

    role: str

    email: str | None = None

    phone: str | None = None

    zone_id: str | None = None

    country: str | None = None

    preferred_language: str = "en"


class AuthResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: AuthUserResponse
