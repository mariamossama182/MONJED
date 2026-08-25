from database.connection import db
from datetime import datetime, timezone
from uuid import uuid4


collection = db["zones"]


def create_zone(zone_data):
    zone = {
        "zone_id": zone_data.get("zone_id", str(uuid4())),
        "name": zone_data["name"],
        "country": zone_data["country"],
        "coordinates": zone_data.get(
            "coordinates",
            {
                "lat": 0,
                "lng": 0
            }
        ),
        "risk_level": zone_data.get("risk_level", ""),
        "created_at": datetime.now(timezone.utc),
    }

    result = collection.insert_one(zone)
    return collection.find_one({"_id": result.inserted_id})


def get_zone(zone_id):
    return collection.find_one({"zone_id": zone_id})


def get_all_zones():
    return list(collection.find())


def update_zone_risk(zone_id, risk_level):
    collection.update_one(
        {"zone_id": zone_id},
        {"$set": {"risk_level": risk_level}}
    )

    return get_zone(zone_id)
