from pydantic import BaseModel, Field


class VolunteerInput(BaseModel):
    name: str = Field(min_length=2)

    zone_id: str = Field(min_length=1)

    available: bool = True

    vehicle_type: str | None = None

    capacity: int = Field(
        default=1,
        ge=1,
    )

    skills: list[str] = Field(
        default_factory=list
    )


class VolunteerRecord(VolunteerInput):
    volunteer_id: str