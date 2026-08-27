"""Citizen + admin auth for MONJED frontend."""

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.mongo_store import mongo_available, strip_mongo_id


router = APIRouter(prefix="/auth", tags=["Auth"])

ADMIN_STAFF_KEY = "MONJED-OPS"

# Fallback when Mongo is unreachable
_MEMORY_USERS: list[dict] = []


class RegisterInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=40)
    password: str = Field(..., min_length=4, max_length=128)
    zone_id: str = Field(..., min_length=1, max_length=64)
    country: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, max_length=8)
    zone: str | None = Field(default=None, max_length=100)
    notification_consent: bool = True


class LoginInput(BaseModel):
    phone: str = Field(..., min_length=7, max_length=40)
    password: str = Field(..., min_length=4, max_length=128)


class AdminLoginInput(BaseModel):
    name: str = Field(default="Operations", max_length=100)
    staff_key: str = Field(..., min_length=4, max_length=64)


class SessionUser(BaseModel):
    role: str
    id: str
    name: str
    phone: str = ""
    email: str = ""
    organization: str = ""
    title: str = ""
    zone_id: str = ""
    country: str = ""
    country_code: str = ""
    zone: str = ""
    notification_consent: bool = True


class AdminProfileUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=120)
    organization: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=100)
    zone: str | None = Field(default=None, max_length=100)


_ADMIN_PROFILE: dict = {
    "role": "admin",
    "id": "admin-ops",
    "name": "Operations",
    "phone": "",
    "email": "",
    "organization": "MONJED Operations",
    "title": "Duty officer",
    "zone_id": "",
    "country": "",
    "country_code": "",
    "zone": "",
    "notification_consent": True,
}


def _public_user(doc: dict) -> SessionUser:
    return SessionUser(
        role=doc.get("role", "user"),
        id=doc.get("user_id") or doc.get("id") or "",
        name=doc.get("name") or "",
        phone=doc.get("phone") or doc.get("phone_number") or "",
        email=doc.get("email") or "",
        organization=doc.get("organization") or "",
        title=doc.get("title") or "",
        zone_id=doc.get("zone_id") or "",
        country=doc.get("country") or "",
        country_code=doc.get("country_code") or "",
        zone=doc.get("zone") or "",
        notification_consent=bool(doc.get("notification_consent", True)),
    )


def _find_user_by_phone(phone: str) -> dict | None:
    phone = (phone or "").strip()
    if not phone:
        return None

    if mongo_available():
        try:
            from database.users_repository import get_users_collection

            collection = get_users_collection()
            doc = collection.find_one(
                {
                    "$or": [
                        {"phone": phone},
                        {"phone_number": phone},
                    ]
                }
            )
            clean = strip_mongo_id(doc)
            if clean:
                return clean
        except Exception as exc:
            print(f"MONJED user lookup warning: {type(exc).__name__}: {exc}")

    for user in _MEMORY_USERS:
        if (user.get("phone") or "").strip() == phone:
            return user
    return None


@router.post("/register", response_model=SessionUser)
def register(data: RegisterInput) -> SessionUser:
    if _find_user_by_phone(data.phone):
        raise HTTPException(status_code=409, detail="Phone already registered.")

    doc = {
        "user_id": f"user-{uuid4()}",
        "role": "user",
        "name": data.name.strip(),
        "phone": data.phone.strip(),
        "password": data.password,
        "zone_id": data.zone_id.strip(),
        "country": (data.country or "").strip(),
        "country_code": (data.country_code or "").strip(),
        "zone": (data.zone or "").strip(),
        "notification_consent": data.notification_consent,
        "notifications_enabled": data.notification_consent,
        "preferred_language": "en",
        "accessibility_needs": [],
    }

    persisted = False
    if mongo_available():
        try:
            from database.users_repository import create_user

            create_user(doc)
            persisted = True
        except Exception as exc:
            print(f"MONJED user persist warning: {type(exc).__name__}: {exc}")

    if not persisted:
        _MEMORY_USERS.append(doc)

    return _public_user(doc)


@router.post("/login", response_model=SessionUser)
def login(data: LoginInput) -> SessionUser:
    user = _find_user_by_phone(data.phone)
    if user is None or (user.get("password") or "") != data.password:
        raise HTTPException(status_code=401, detail="Invalid phone or password.")
    return _public_user(user)


@router.post("/admin", response_model=SessionUser)
def admin_login(data: AdminLoginInput) -> SessionUser:
    if data.staff_key.strip() != ADMIN_STAFF_KEY:
        raise HTTPException(status_code=401, detail="Invalid staff key.")
    name = (data.name or "").strip()
    if name:
        _ADMIN_PROFILE["name"] = name
    return _public_user(_ADMIN_PROFILE)


@router.get("/admin/profile", response_model=SessionUser)
def get_admin_profile() -> SessionUser:
    return _public_user(_ADMIN_PROFILE)


@router.put("/admin/profile", response_model=SessionUser)
def update_admin_profile(data: AdminProfileUpdate) -> SessionUser:
    _ADMIN_PROFILE.update(
        {
            "name": data.name.strip(),
            "phone": (data.phone or "").strip(),
            "email": (data.email or "").strip(),
            "organization": (data.organization or "").strip(),
            "title": (data.title or "").strip(),
            "country": (data.country or "").strip(),
            "zone": (data.zone or "").strip(),
        }
    )
    return _public_user(_ADMIN_PROFILE)


class ContactInput(BaseModel):
    topic: str = Field(default="technical", max_length=40)
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(default="", max_length=120)
    phone: str = Field(default="", max_length=40)
    message: str = Field(..., min_length=3, max_length=2000)


_CONTACT_MESSAGES: list[dict] = []


def _contact_collection():
    from database.connection import get_database

    return get_database()["contact_messages"]


@router.post("/contact")
def submit_contact(data: ContactInput) -> dict:
    if not (data.email or "").strip() and not (data.phone or "").strip():
        raise HTTPException(
            status_code=422,
            detail="Provide an email or phone number so we can reply.",
        )
    doc = {
        "id": f"contact-{uuid4()}",
        "topic": data.topic.strip() or "technical",
        "name": data.name.strip(),
        "email": (data.email or "").strip(),
        "phone": (data.phone or "").strip(),
        "message": data.message.strip(),
    }

    if mongo_available():
        try:
            _contact_collection().insert_one(dict(doc))
            return {"status": "ok", "id": doc["id"], "message": "Message received."}
        except Exception as exc:
            print(f"MONJED contact persist warning: {type(exc).__name__}: {exc}")

    _CONTACT_MESSAGES.append(doc)
    return {"status": "ok", "id": doc["id"], "message": "Message received."}


@router.get("/contact")
def list_contact_messages() -> list[dict]:
    """Ops inbox for contact form messages."""
    if mongo_available():
        try:
            docs = list(_contact_collection().find().sort("_id", -1))
            return [strip_mongo_id(d) or {} for d in docs]
        except Exception as exc:
            print(f"MONJED contact list warning: {type(exc).__name__}: {exc}")
    return list(reversed(_CONTACT_MESSAGES))
