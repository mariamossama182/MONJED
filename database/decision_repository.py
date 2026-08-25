from database.connection import db
from datetime import datetime, timezone
from uuid import uuid4


collection = db["decisions"]


def create_decision(decision_data):
    decision = {
        "decision_id": str(uuid4()),
        "zone_id": decision_data["zone_id"],
        "risk_id": decision_data["risk_id"],
        "hazard": decision_data["hazard"],
        "risk_score": decision_data["risk_score"],
        "risk_level": decision_data["risk_level"],
        "confidence": decision_data["confidence"],
        "decision_status": decision_data["decision_status"],
        "current_action": decision_data.get("current_action", ""),
        "backup_action": decision_data.get("backup_action", ""),
        "reasons": decision_data.get("reasons", []),
        "evidence_used": decision_data.get("evidence_used", 0),
        "source_report_ids": decision_data.get("source_report_ids", []),
        "created_at": datetime.now(timezone.utc),
    }

    result = collection.insert_one(decision)
    return collection.find_one({"_id": result.inserted_id})


def get_decision(decision_id):
    return collection.find_one({"decision_id": decision_id})


def get_decisions_by_zone(zone_id):
    return list(
        collection.find({"zone_id": zone_id})
        .sort("created_at", -1)
    )
    
