from database.connection import get_database



def get_users_collection():

    db = get_database()

    return db["users"]



def create_user(data):

    collection = get_users_collection()

    collection.insert_one(data)

    return data["user_id"]



def get_user(user_id):

    collection = get_users_collection()

    return collection.find_one(
        {
            "user_id": user_id
        }
    )



def get_all_users():

    collection = get_users_collection()

    return list(
        collection.find()
    )



def update_user(
    user_id,
    data
):

    collection = get_users_collection()

    result = collection.update_one(
        {
            "user_id": user_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_user(user_id):

    collection = get_users_collection()

    result = collection.delete_one(
        {
            "user_id": user_id
        }
    )

    return result.deleted_count