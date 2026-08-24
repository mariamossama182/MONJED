from connection import get_database


def create_indexes():
    db = get_database()

    # =========================
    # Risk Snapshots
    # =========================

    risk_snapshots = db["risk_snapshots"]

    risk_snapshots.create_index([
        ("country", 1),
        ("zone", 1),
        ("hazard", 1)
    ])

    risk_snapshots.create_index([
        ("created_at", -1)
    ])

    risk_snapshots.create_index([
        ("hazard", 1),
        ("created_at", -1)
    ])


    # =========================
    # Community Reports
    # =========================

    community_reports = db["community_reports"]

    community_reports.create_index([
        ("country", 1),
        ("zone", 1)
    ])

    community_reports.create_index([
        ("status", 1)
    ])

    community_reports.create_index([
        ("created_at", -1)
    ])

    community_reports.create_index([
        ("location", "2dsphere")
    ])


    # =========================
    # Volunteers
    # =========================

    volunteers = db["volunteers"]

    volunteers.create_index([
        ("country", 1),
        ("zone", 1)
    ])

    volunteers.create_index([
        ("available", 1)
    ])

    volunteers.create_index([
        ("location", "2dsphere")
    ])


    # =========================
    # Assistance Requests
    # =========================

    assistance_requests = db["assistance_requests"]

    assistance_requests.create_index([
        ("country", 1),
        ("zone", 1)
    ])

    assistance_requests.create_index([
        ("status", 1)
    ])

    assistance_requests.create_index([
        ("priority", -1)
    ])

    assistance_requests.create_index([
        ("created_at", -1)
    ])


    # =========================
    # AI Decisions
    # =========================

    ai_decisions = db["ai_decisions"]

    ai_decisions.create_index([
        ("hazard", 1),
        ("country", 1)
    ])

    ai_decisions.create_index([
        ("created_at", -1)
    ])

    ai_decisions.create_index([
        ("validation_status", 1)
    ])


    # =========================
    # Alerts
    # =========================

    alerts = db["alerts"]

    alerts.create_index([
        ("country", 1),
        ("hazard", 1)
    ])

    alerts.create_index([
        ("status", 1)
    ])

    alerts.create_index([
        ("created_at", -1)
    ])


    # =========================
    # Users
    # =========================

    users = db["users"]

    users.create_index([
        ("phone", 1)
    ], unique=True)

    users.create_index([
        ("country", 1),
        ("zone", 1)
    ])

    print("Indexes created successfully!")
