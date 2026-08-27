from uuid import uuid4

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
)
from app.services.mongo_store import dump_record, mongo_available, strip_mongo_id


_volunteers: list[VolunteerRecord] = []


def _normalize_skills(skills: list[str]) -> list[str]:
    return list(
        dict.fromkeys(skill.strip() for skill in skills if skill.strip())
    )


def _from_doc(doc: dict | None) -> VolunteerRecord | None:
    clean = strip_mongo_id(doc)
    if not clean:
        return None
    try:
        return VolunteerRecord.model_validate(clean)
    except Exception:
        return None


def _load_all_mongo() -> list[VolunteerRecord]:
    from database.volunteers_repository import get_all_volunteers as mongo_get_all

    records = []
    for doc in mongo_get_all() or []:
        record = _from_doc(doc)
        if record is not None:
            records.append(record)
    return records


def add_volunteer(data: VolunteerInput) -> VolunteerRecord:
    """
    Register volunteer or trained responder.

    GPS coordinates are stored for responder matching.
    """
    volunteer_data = data.model_dump()
    volunteer_data["zone_id"] = data.zone_id.strip()
    volunteer_data["name"] = data.name.strip()
    if data.vehicle_type:
        volunteer_data["vehicle_type"] = data.vehicle_type.strip()
    volunteer_data["skills"] = _normalize_skills(data.skills)

    volunteer = VolunteerRecord(
        volunteer_id=str(uuid4()),
        **volunteer_data,
    )

    if mongo_available():
        try:
            from database.volunteers_repository import create_volunteer

            create_volunteer(dump_record(volunteer))
            return volunteer
        except Exception as exc:
            print(f"MONJED volunteer persist warning: {type(exc).__name__}: {exc}")

    _volunteers.append(volunteer)
    return volunteer


def get_volunteer(volunteer_id: str) -> VolunteerRecord | None:
    volunteer_id = (volunteer_id or "").strip()
    if not volunteer_id:
        return None

    if mongo_available():
        try:
            from database.volunteers_repository import get_volunteer as mongo_get

            record = _from_doc(mongo_get(volunteer_id))
            if record is not None:
                return record
        except Exception as exc:
            print(f"MONJED volunteer get warning: {type(exc).__name__}: {exc}")

    for volunteer in _volunteers:
        if volunteer.volunteer_id == volunteer_id:
            return volunteer
    return None


def get_available_volunteers(zone_id: str) -> list[VolunteerRecord]:
    """
    Returns available volunteers in same zone.

    Qualification and distance ranking are handled
    by volunteer_matching engine.
    """
    zone_id = zone_id.strip()
    return [
        volunteer
        for volunteer in get_all_volunteers()
        if volunteer.available and volunteer.zone_id.strip() == zone_id
    ]


def set_volunteer_availability(
    volunteer_id: str,
    available: bool,
) -> VolunteerRecord | None:
    volunteer = get_volunteer(volunteer_id)
    if volunteer is None:
        return None

    updated = volunteer.model_copy(update={"available": available})

    if mongo_available():
        try:
            from database.volunteers_repository import update_volunteer

            update_volunteer(volunteer_id, {"available": available})
            return updated
        except Exception as exc:
            print(
                f"MONJED volunteer availability warning: {type(exc).__name__}: {exc}"
            )

    for i, existing in enumerate(_volunteers):
        if existing.volunteer_id == volunteer_id:
            _volunteers[i] = updated
            return updated
    _volunteers.append(updated)
    return updated


def get_all_volunteers() -> list[VolunteerRecord]:
    if mongo_available():
        try:
            return _load_all_mongo()
        except Exception as exc:
            print(f"MONJED volunteer list warning: {type(exc).__name__}: {exc}")
    return list(_volunteers)


def get_volunteer_by_phone(phone: str) -> VolunteerRecord | None:
    phone = (phone or "").strip()
    if not phone:
        return None
    for volunteer in get_all_volunteers():
        if (volunteer.phone or "").strip() == phone:
            return volunteer
    return None


def to_public(volunteer: VolunteerRecord) -> dict:
    data = volunteer.model_dump()
    data.pop("password", None)
    return data


def clear_volunteers():
    _volunteers.clear()
    if mongo_available():
        try:
            from database.volunteers_repository import get_volunteer_collection

            get_volunteer_collection().delete_many({})
        except Exception as exc:
            print(f"MONJED volunteer clear warning: {type(exc).__name__}: {exc}")
