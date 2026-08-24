from bson import ObjectId
from connection import get_database


def get_volunteer_collection():
    db = get_database()
    return db["volunteers"]


def create_volunteers(data):
    collection = get_volunteer_collection()

    result = collection.insert_one(data)

    return str(result.inserted_id)


def get_volunteers(volunteer_id):
    collection = get_volunteers_collection()

    return collection.find_one({
        "_id": ObjectId(volunteer_id)
    })


def get_all_volunteer():
    collection = get_volunteers_collection()

    return list(collection.find())


def update_volunteer(volunteer_id, data):
    collection = get_volunteers_collection()

    result = collection.update_one(
        {"_id": ObjectId(volunteer_id)},
        {"$set": data}
    )

    return result.modified_count


def delete_volunteer(volunteer_id):
    collection = get_volunteer_collection()

    result = collection.delete_one({
        "_id": ObjectId(volunteer_id)
    })

    return result.deleted_count
