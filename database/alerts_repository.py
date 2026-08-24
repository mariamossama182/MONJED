from bson import ObjectId
from connection import get_database


def get_alerts_collection():
    db = get_database()
    return db["alerts"]


def create_alerts(data):
    collection = get_alerts_collection()

    result = collection.insert_one(data)

    return str(result.inserted_id)


def get_alerts(alerts_id):
    collection = get_alerts_collection()

    return collection.find_one({
        "_id": ObjectId(alerts_id)
    })


def get_all_alerts():
    collection = get_alerts_collection()

    return list(collection.find())


def update_alerts(alerts_id, data):
    collection = get_alerts_collection()

    result = collection.update_one(
        {"_id": ObjectId(alerts_id)},
        {"$set": data}
    )

    return result.modified_count


def delete_alerts(alerts_id):
    collection = get_alerts_collection()

    result = collection.delete_one({
        "_id": ObjectId(alerts_id)
    })

    return result.deleted_count
