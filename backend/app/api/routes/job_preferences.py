
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.job_preference import (
    JobPreferenceCreate,
    JobPreferenceUpdate,
    JobPreferenceResponse,
)
from app.services.job_preference_service import (
    get_user_preferences,
    create_job_preference,
    update_job_preference,
    delete_job_preference,
)

router = APIRouter()


@router.get(
    "/",
    response_model=list[JobPreferenceResponse],
)
def list_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_preferences(db, current_user.id)


@router.post(
    "/",
    response_model=JobPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_preference(
    preference_data: JobPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_job_preference(
        db,
        current_user.id,
        preference_data,
    )


@router.patch(
    "/{preference_id}",
    response_model=JobPreferenceResponse,
)
def update_preference(
    preference_id: UUID,
    preference_data: JobPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        preference = update_job_preference(
            db,
            current_user.id,
            preference_id,
            preference_data,
        )

        if preference is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job preference not found.",
            )

        return preference

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.delete(
    "/{preference_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_preference(
    preference_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_job_preference(
        db,
        current_user.id,
        preference_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preference not found.",
        )

    return None
