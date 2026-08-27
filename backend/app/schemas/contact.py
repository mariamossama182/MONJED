from datetime import datetime

from pydantic import BaseModel, Field


class ContactRequest(BaseModel):

    name: str = Field(
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

    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    subject: str | None = Field(
        default=None,
        max_length=150,
    )

    message: str = Field(
        ...,
        min_length=5,
        max_length=2000,
    )


class ContactResponse(BaseModel):

    contact_id: str

    status: str = "received"

    created_at: datetime
