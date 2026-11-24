
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import CandidateProfile
from app.schemas.profile import CandidateProfileUpdate


def get_candidate_profile(
    db: Session,
    user_id,
) -> CandidateProfile | None:
    """Retrieve a candidate profile belonging to a specific user."""

    return db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == user_id
        )
    )


def update_candidate_profile(
    db: Session,
    user_id,
    profile_data: CandidateProfileUpdate,
) -> CandidateProfile:
    """Update only the profile belonging to the authenticated user."""

    profile = get_candidate_profile(db, user_id)

    if profile is None:
        raise ValueError("Candidate profile not found.")

    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    try:
        db.commit()
        db.refresh(profile)
        return profile

    except Exception:
        db.rollback()
        raise
