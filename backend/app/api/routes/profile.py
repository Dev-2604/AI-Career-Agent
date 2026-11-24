
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.profile import (
    CandidateProfileUpdate,
    CandidateProfileResponse,
)
from app.services.profile_service import (
    get_candidate_profile,
    update_candidate_profile,
)

router = APIRouter()


@router.get(
    "/me",
    response_model=CandidateProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_candidate_profile(db, current_user.id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )

    return profile


@router.patch(
    "/me",
    response_model=CandidateProfileResponse,
)
def update_my_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_candidate_profile(
            db,
            current_user.id,
            profile_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

