from database.connection import get_database


def get_users_collection():

    db = get_database()

    return db["users"]


def create_user(data):

    collection = get_users_collection()

    collection.insert_one(
        data
    )

    return data[
        "user_id"
    ]


def get_user(
    user_id,
):

    collection = get_users_collection()

    return collection.find_one(
        {
            "user_id":
                user_id
        }
    )


def get_all_users():

    collection = get_users_collection()

    return list(
        collection.find()
    )


def get_users_by_zone(
    zone_id,
):

    collection = get_users_collection()

    return list(
        collection.find(
            {
                "zone_id":
                    zone_id
            }
        )
    )


def get_alert_recipients_by_zone(
    zone_id,
):
    """
    Return users who explicitly consented to notifications
    and have a valid stored phone number.

    Supports both:
    - phone
    - phone_number

    for compatibility with existing records.
    """

    collection = get_users_collection()

    users = list(
        collection.find(
            {
                "zone_id":
                    zone_id,

                "$and": [

                    {
                        "$or": [
                            {
                                "notification_consent":
                                    True
                            },
                            {
                                "notifications_enabled":
                                    True
                            },
                        ]
                    },

                    {
                        "$or": [
                            {
                                "phone": {
                                    "$exists":
                                        True,
                                    "$nin": [
                                        None,
                                        "",
                                    ],
                                }
                            },
                            {
                                "phone_number": {
                                    "$exists":
                                        True,
                                    "$nin": [
                                        None,
                                        "",
                                    ],
                                }
                            },
                        ]
                    },
                ]
            }
        )
    )

    recipients = []

    for user in users:

        phone = (
            user.get(
                "phone"
            )
            or user.get(
                "phone_number"
            )
        )

        if not phone:
            continue

        recipients.append(
            {
                "user_id":
                    user.get(
                        "user_id"
                    ),

                "phone":
                    phone,

                "zone_id":
                    user.get(
                        "zone_id"
                    ),

                "preferred_language":
                    user.get(
                        "preferred_language",
                        "en",
                    ),

                "accessibility_needs":
                    user.get(
                        "accessibility_needs",
                        [],
                    ),
            }
        )

    return recipients


def get_recipient_phone_numbers(
    zone_id,
):

    recipients = (
        get_alert_recipients_by_zone(
            zone_id
        )
    )

    numbers = []

    for recipient in recipients:

        phone = recipient[
            "phone"
        ]

        if phone not in numbers:
            numbers.append(
                phone
            )

    return numbers


def update_user(
    user_id,
    data,
):

    collection = get_users_collection()

    result = collection.update_one(
        {
            "user_id":
                user_id
        },
        {
            "$set":
                data
        }
    )

    return result.modified_count


def delete_user(
    user_id,
):

    collection = get_users_collection()

    result = collection.delete_one(
        {
            "user_id":
                user_id
        }
    )

    return result.deleted_count