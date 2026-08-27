from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdate,
)

from database.users_repository import (
    get_user,
    update_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users & Profiles"],
)


# ============================================================
# PROFILE SERIALIZATION
# ============================================================

def _build_profile(
    user: dict,
) -> UserProfileResponse:
    """
    Return only frontend-safe profile information.

    Private delivery fields such as phone numbers
    are intentionally excluded.
    """

    notification_consent = bool(
        user.get(
            "notification_consent",
            user.get(
                "notifications_enabled",
                False,
            ),
        )
    )

    return UserProfileResponse(
        user_id=str(
            user.get(
                "user_id",
                "",
            )
        ),

        display_name=(
            user.get(
                "display_name"
            )
            or user.get(
                "name"
            )
        ),

        role=user.get(
            "role"
        ),

        zone_id=user.get(
            "zone_id"
        ),

        preferred_language=user.get(
            "preferred_language",
            "en",
        ),

        accessibility_needs=list(
            user.get(
                "accessibility_needs",
                [],
            )
            or []
        ),

        notification_consent=notification_consent,
    )


# ============================================================
# GET PROFILE
# ============================================================

@router.get(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
)
def read_user_profile(
    user_id: str,
) -> UserProfileResponse:

    user = get_user(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return _build_profile(
        user
    )


# ============================================================
# UPDATE PROFILE
# ============================================================

@router.patch(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
)
def update_user_profile(
    user_id: str,
    data: UserProfileUpdate,
) -> UserProfileResponse:

    existing_user = get_user(
        user_id
    )

    if existing_user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    updates = data.model_dump(
        exclude_none=True
    )

    # --------------------------------------------------------
    # Normalize simple text fields
    # --------------------------------------------------------

    if "display_name" in updates:

        updates["display_name"] = (
            updates[
                "display_name"
            ]
            .strip()
        )

    if "zone_id" in updates:

        updates["zone_id"] = (
            updates[
                "zone_id"
            ]
            .strip()
        )

    # --------------------------------------------------------
    # Remove duplicate accessibility values
    # --------------------------------------------------------

    if "accessibility_needs" in updates:

        updates[
            "accessibility_needs"
        ] = list(
            dict.fromkeys(
                updates[
                    "accessibility_needs"
                ]
            )
        )

    # --------------------------------------------------------
    # Keep legacy notification field synchronized
    #
    # Recipient selection currently supports both:
    # notification_consent
    # notifications_enabled
    # --------------------------------------------------------

    if "notification_consent" in updates:

        consent = bool(
            updates[
                "notification_consent"
            ]
        )

        updates[
            "notification_consent"
        ] = consent

        updates[
            "notifications_enabled"
        ] = consent

    if updates:

        update_user(
            user_id,
            updates,
        )

    updated_user = get_user(
        user_id
    )

    if updated_user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return _build_profile(
        updated_user
    )
