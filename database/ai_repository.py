from bson import ObjectId
from connection import get_database


def get_ai_collection():
    db = get_database()
    return db["ai_decisions"]


def create_ai(data):
    collection = get_ai_collection()

    result = collection.insert_one(data)

    return str(result.inserted_id)


def get_ai(ai_id):
    collection = get_volunteers_collection()

    return collection.find_one({
        "_id": ObjectId(ai_id)
    })


def get_all_ai():
    collection = get_ai_collection()

    return list(collection.find())


def update_ai(ai_id, data):
    collection = get_ai_collection()

    result = collection.update_one(
        {"_id": ObjectId(ai_id)},
        {"$set": data}
    )

    return result.modified_count


def delete_ai(ai_id):
    collection = get_ai_collection()

    result = collection.delete_one({
        "_id": ObjectId(ai_id)
    })

    return result.deleted_count
