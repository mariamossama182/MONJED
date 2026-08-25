from database.connection import get_database


def get_risk_collection():
    db = get_database()
    return db["risk_snapshots"]



def create_risk_snapshot(data):

    collection = get_risk_collection()

    collection.insert_one(data)

    return data["risk_id"]



def get_risk_snapshot(risk_id):

    collection = get_risk_collection()

    return collection.find_one(
        {
            "risk_id": risk_id
        }
    )



def get_all_risk_snapshots():

    collection = get_risk_collection()

    return list(
        collection.find()
    )



def delete_risk_snapshot(risk_id):

    collection = get_risk_collection()

    result = collection.delete_one(
        {
            "risk_id": risk_id
        }
    )

    return result.deleted_count