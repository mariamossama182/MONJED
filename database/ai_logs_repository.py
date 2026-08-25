from database.connection import db
from datetime import datetime, timezone
from uuid import uuid4


collection = db["ai_logs"]


def create_ai_log(log_data):
    log = {
        "log_id": str(uuid4()),
        "model": log_data["model"],
        "input": log_data.get("input", {}),
        "output": log_data.get("output", {}),
        "confidence": log_data.get("confidence"),
        "created_at": datetime.now(timezone.utc),
    }

    result = collection.insert_one(log)
    return collection.find_one({"_id": result.inserted_id})


def get_ai_log(log_id):
    return collection.find_one({
        "log_id": log_id
    })


def get_ai_logs_by_model(model):
    return list(
        collection.find({"model": model})
        .sort("created_at", -1)
    )
