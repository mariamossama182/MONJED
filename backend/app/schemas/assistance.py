from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RequestPriority = Literal[
    "low",
    "moderate",
    "high",
    "critical",
]

RequestStatus = Literal[
    "pending",
    "assigned",
    "in_progress",
    "resolved",
]


class AssistanceRequestInput(BaseModel):
    zone_id: str = Field(min_length=1)
    location: str = Field(min_length=2)

    hazard: Literal[
        "flood",
        "earthquake",
    ]

    request_type: Literal[
        "evacuation",
        "transportation",
        "mobility_assistance",
        "medical_support",
        "rescue_support",
        "other",
    ]

    priority: RequestPriority

    description: str = Field(
        min_length=3,
        max_length=500,
    )


class AssistanceRequestRecord(BaseModel):
    request_id: str

    zone_id: str
    location: str
    hazard: str

    request_type: str
    priority: RequestPriority

    description: str

    status: RequestStatus = "pending"

    assigned_volunteer_id: str | None = None

    created_at: datetime
    assigned_at: datetime | None = None
    resolved_at: datetime | None = None