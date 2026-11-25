
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import (
    upload_resume,
    get_user_resumes,
    delete_resume,
    set_default_resume,
)

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_my_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await upload_resume(
        db,
        current_user.id,
        file,
    )


@router.get(
    "/",
    response_model=list[ResumeResponse],
)
def list_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_resumes(db, current_user.id)


@router.patch(
    "/{resume_id}/default",
    response_model=ResumeResponse,
)
def make_resume_default(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = set_default_resume(
        db,
        current_user.id,
        resume_id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    return resume


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_resume(
        db,
        current_user.id,
        resume_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    return None
