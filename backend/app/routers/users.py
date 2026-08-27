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


def _mask_phone(
    phone: str | None,
) -> str | None:
    """
    Return a masked international phone number.

    Full phone numbers remain stored in MongoDB for
    notification delivery but are not exposed to frontend.

    ASCII asterisks are intentionally used to avoid
    terminal/browser encoding inconsistencies.
    """

    if not phone:
        return None

    value = str(
        phone
    ).strip()

    if not value.startswith("+"):
        return None

    digits = value[1:]

    if len(digits) <= 6:
        return "+****"

    visible_start = digits[:4]
    visible_end = digits[-2:]

    hidden_length = max(
        len(digits) - 6,
        2,
    )

    return (
        "+"
        + visible_start
        + ("*" * hidden_length)
        + visible_end
    )


def _clean_optional_text(
    value,
) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip()

    return cleaned or None


def _build_profile(
    user: dict,
) -> UserProfileResponse:
    """
    Build a frontend-safe profile for citizens,
    volunteers, and admin/operations users.
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

    stored_phone = (
        user.get("phone")
        or user.get("phone_number")
    )

    return UserProfileResponse(
        user_id=str(
            user.get(
                "user_id",
                "",
            )
        ),

        display_name=(
            user.get("display_name")
            or user.get("name")
        ),

        role=user.get("role"),

        role_title=user.get(
            "role_title"
        ),

        organization=user.get(
            "organization"
        ),

        work_email=(
            user.get("work_email")
            or user.get("email")
        ),

        phone=_mask_phone(
            stored_phone
        ),

        zone_id=user.get(
            "zone_id"
        ),

        country=user.get(
            "country"
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

    text_fields = {
        "display_name",
        "role_title",
        "organization",
        "work_email",
        "phone",
        "zone_id",
        "country",
    }

    for field_name in text_fields:
        if field_name in updates:
            cleaned = _clean_optional_text(
                updates[field_name]
            )

            if cleaned is not None:
                updates[
                    field_name
                ] = cleaned

    if "work_email" in updates:
        updates[
            "work_email"
        ] = updates[
            "work_email"
        ].lower()

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
