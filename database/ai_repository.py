from database.connection import get_database



def get_ai_collection():

    db = get_database()

    return db["ai_decisions"]



def create_ai(data):

    collection = get_ai_collection()

    collection.insert_one(data)

    return data["decision_id"]



def get_ai(decision_id):

    collection = get_ai_collection()

    return collection.find_one(
        {
            "decision_id": decision_id
        }
    )



def get_all_ai():

    collection = get_ai_collection()

    return list(
        collection.find()
    )



def update_ai(
    decision_id,
    data
):

    collection = get_ai_collection()

    result = collection.update_one(
        {
            "decision_id": decision_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_ai(decision_id):

    collection = get_ai_collection()

    result = collection.delete_one(
        {
            "decision_id": decision_id
        }
    )

    return result.deleted_count