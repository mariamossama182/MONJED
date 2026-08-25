from database.connection import db
from datetime import datetime, timezone
from uuid import uuid4


collection = db["accessibility_profiles"]


def create_accessibility_profile(profile_data):
    profile = {
        "profile_id": str(uuid4()),
        "user_id": profile_data["user_id"],
        "needs": profile_data.get("needs", []),
        "preferred_language": profile_data.get(
            "preferred_language",
            "en"
        ),
        "communication_methods": profile_data.get(
            "communication_methods",
            []
        ),
        "created_at": datetime.now(timezone.utc),
    }

    result = collection.insert_one(profile)
    return collection.find_one({"_id": result.inserted_id})


def get_profile_by_user(user_id):
    return collection.find_one({
        "user_id": user_id
    })


def update_accessibility_profile(user_id, data):
    collection.update_one(
        {"user_id": user_id},
        {"$set": data}
    )

    return get_profile_by_user(user_id)
