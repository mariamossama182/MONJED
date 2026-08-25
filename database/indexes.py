from database.connection import get_database



def create_indexes():

    db = get_database()


    # =========================
    # Risk Snapshots
    # =========================

    risk = db["risk_snapshots"]

    risk.create_index(
        [
            ("zone_id", 1),
            ("hazard", 1)
        ]
    )

    risk.create_index(
        [
            ("created_at", -1)
        ]
    )


    # =========================
    # Community Reports
    # =========================

    reports = db["community_reports"]

    reports.create_index(
        [
            ("zone_id", 1),
            ("created_at", -1)
        ]
    )

    reports.create_index(
        [
            ("hazard_type",1)
        ]
    )


    # =========================
    # Assistance Requests
    # =========================

    requests = db["assistance_requests"]

    requests.create_index(
        [
            ("zone_id",1),
            ("status",1)
        ]
    )

    requests.create_index(
        [
            ("priority",-1)
        ]
    )

    requests.create_index(
        [
            ("created_at",-1)
        ]
    )


    # =========================
    # Volunteers
    # =========================

    volunteers = db["volunteers"]

    volunteers.create_index(
        [
            ("zone_id",1),
            ("available",1)
        ]
    )


    # =========================
    # AI Decisions
    # =========================

    decisions = db["ai_decisions"]

    decisions.create_index(
        [
            ("zone_id",1),
            ("hazard",1)
        ]
    )

    decisions.create_index(
        [
            ("created_at",-1)
        ]
    )


    # =========================
    # Alerts
    # =========================

    alerts = db["alerts"]

    alerts.create_index(
        [
            ("zone_id",1),
            ("hazard",1)
        ]
    )

    alerts.create_index(
        [
            ("created_at",-1)
        ]
    )


    # =========================
    # Users
    # =========================

    users = db["users"]

    users.create_index(
        [
            ("phone",1)
        ],
        unique=True
    )


    # =========================
    # Zones
    # =========================

    zones = db["zones"]

    zones.create_index(
        [
            ("zone_id",1)
        ],
        unique=True
    )


    # =========================
    # Translations
    # =========================

    translations = db["translations"]

    translations.create_index(
        [
            ("key",1),
            ("language",1)
        ],
        unique=True
    )


    # =========================
    # Accessibility
    # =========================

    accessibility = db["accessibility_profiles"]

    accessibility.create_index(
        [
            ("user_id",1)
        ]
    )


    print(
        "Indexes created successfully!"
    )