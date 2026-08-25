from database.connection import get_database



def get_alerts_collection():

    db = get_database()

    return db["alerts"]



def create_alert(data):

    collection = get_alerts_collection()

    collection.insert_one(data)

    return data["alert_id"]



def get_alert(alert_id):

    collection = get_alerts_collection()

    return collection.find_one(
        {
            "alert_id": alert_id
        }
    )



def get_all_alerts():

    collection = get_alerts_collection()

    return list(
        collection.find()
    )



def update_alert(
    alert_id,
    data
):

    collection = get_alerts_collection()

    result = collection.update_one(
        {
            "alert_id": alert_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_alert(alert_id):

    collection = get_alerts_collection()

    result = collection.delete_one(
        {
            "alert_id": alert_id
        }
    )

    return result.deleted_count