from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "monjed"

client = None
db = None


def connect_to_mongodb():
    global client, db

    try:
        client = MongoClient(MONGO_URI)

        # اختبار الاتصال
        client.admin.command("ping")

        db = client[DB_NAME]

        print("MongoDB connected successfully!")

        return db

    except PyMongoError as e:
        print("MongoDB connection failed!")
        print(e)

        client = None
        db = None

        return None


def get_database():
    global db

    if db is None:
        connect_to_mongodb()

    return db


def close_connection():
    global client

    if client:
        client.close()
        print("MongoDB connection closed.")
