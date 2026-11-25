
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import JobPreference
from app.schemas.job_preference import (
    JobPreferenceCreate,
    JobPreferenceUpdate,
)


def get_user_preferences(
    db: Session,
    user_id: UUID,
) -> list[JobPreference]:
    """Retrieve all preferences belonging to a user."""

    return list(
        db.scalars(
            select(JobPreference)
            .where(JobPreference.user_id == user_id)
            .order_by(JobPreference.created_at.desc())
        ).all()
    )


def get_preference_by_id(
    db: Session,
    user_id: UUID,
    preference_id: UUID,
) -> JobPreference | None:
    """Retrieve one preference owned by a specific user."""

    return db.scalar(
        select(JobPreference).where(
            JobPreference.id == preference_id,
            JobPreference.user_id == user_id,
        )
    )


def create_job_preference(
    db: Session,
    user_id: UUID,
    preference_data: JobPreferenceCreate,
) -> JobPreference:
    """Create a new job preference for a user."""

    preference = JobPreference(
        user_id=user_id,
        **preference_data.model_dump(),
    )

    db.add(preference)

    try:
        db.commit()
        db.refresh(preference)
        return preference

    except Exception:
        db.rollback()
        raise


def update_job_preference(
    db: Session,
    user_id: UUID,
    preference_id: UUID,
    preference_data: JobPreferenceUpdate,
) -> JobPreference | None:
    """Update a preference only if it belongs to the user."""

    preference = get_preference_by_id(
        db,
        user_id,
        preference_id,
    )

    if preference is None:
        return None

    update_data = preference_data.model_dump(
        exclude_unset=True
    )

    # Prevent setting a required database field to NULL.
    if "target_role" in update_data and update_data["target_role"] is None:
        raise ValueError("Target role cannot be empty.")

    # Validate the resulting salary range, including existing values.
    new_min = update_data.get("min_salary", preference.min_salary)
    new_max = update_data.get("max_salary", preference.max_salary)

    if new_min is not None and new_max is not None:
        if new_min > new_max:
            raise ValueError(
                "Minimum salary cannot exceed maximum salary."
            )

    for field, value in update_data.items():
        setattr(preference, field, value)

    try:
        db.commit()
        db.refresh(preference)
        return preference

    except Exception:
        db.rollback()
        raise


def delete_job_preference(
    db: Session,
    user_id: UUID,
    preference_id: UUID,
) -> bool:
    """Delete a preference only if it belongs to the user."""

    preference = get_preference_by_id(
        db,
        user_id,
        preference_id,
    )

    if preference is None:
        return False

    try:
        db.delete(preference)
        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
