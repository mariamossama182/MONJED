from database.connection import db
from datetime import datetime, timezone


collection = db["translations"]


def create_translation(key, language, text):
    translation = {
        "key": key,
        "language": language,
        "text": text,
        "created_at": datetime.now(timezone.utc),
    }

    result = collection.insert_one(translation)
    return collection.find_one({"_id": result.inserted_id})


def get_translation(key, language):
    return collection.find_one({
        "key": key,
        "language": language
    })


def get_translations_by_language(language):
    return list(
        collection.find({"language": language})
    )


def update_translation(key, language, text):
    collection.update_one(
        {
            "key": key,
            "language": language
        },
        {
            "$set": {
                "text": text
            }
        }
    )

    return get_translation(key, language)
