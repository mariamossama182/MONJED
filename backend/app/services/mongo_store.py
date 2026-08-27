"""Shared helpers for Mongo-backed app stores."""

from __future__ import annotations

from typing import Any

_mongo_ok: bool | None = None


def mongo_available() -> bool:
    global _mongo_ok
    if _mongo_ok is True:
        return True
    try:
        from database.connection import get_database

        get_database()
        _mongo_ok = True
        return True
    except Exception as exc:
        if _mongo_ok is not False:
            print(f"MONJED Mongo unavailable: {type(exc).__name__}: {exc}")
        _mongo_ok = False
        return False


def strip_mongo_id(doc: dict | None) -> dict | None:
    if not doc:
        return None
    clean = dict(doc)
    clean.pop("_id", None)
    return clean


def dump_record(record: Any) -> dict:
    """Serialize a Pydantic model for Mongo insert/update."""
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return dict(record)
