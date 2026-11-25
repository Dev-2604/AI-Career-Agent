
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Resume
from app.services.resume_storage_service import (
    save_resume_file,
    delete_resume_file,
)
from app.services.resume_parser_service import extract_resume_text


async def upload_resume(
    db: Session,
    user_id: UUID,
    file: UploadFile,
) -> Resume:
    """Upload, parse, and save a resume for the authenticated user."""

    stored_file = await save_resume_file(user_id, file)

    try:
        parsed_content = extract_resume_text(
            stored_file["file_path"]
        )

        if not parsed_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text found in the uploaded resume.",
            )

        resume = Resume(
            user_id=user_id,
            filename=stored_file["original_filename"],
            storage_path=stored_file["file_path"],
            file_type=stored_file["file_extension"].lstrip("."),
            parsed_content=parsed_content,
            is_default=False,
            version=1,
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    except Exception:
        db.rollback()
        delete_resume_file(stored_file["file_path"])
        raise


def get_user_resumes(
    db: Session,
    user_id: UUID,
) -> list[Resume]:
    """Return all resumes belonging to the authenticated user."""

    return list(
        db.scalars(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        ).all()
    )


def get_resume_by_id(
    db: Session,
    user_id: UUID,
    resume_id: UUID,
) -> Resume | None:
    """Retrieve a resume only if it belongs to the user."""

    return db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
    )


def delete_resume(
    db: Session,
    user_id: UUID,
    resume_id: UUID,
) -> bool:
    """Delete a resume belonging to the authenticated user."""

    resume = get_resume_by_id(db, user_id, resume_id)

    if resume is None:
        return False

    file_path = resume.storage_path

    try:
        db.delete(resume)
        db.commit()

        delete_resume_file(file_path)

        return True

    except Exception:
        db.rollback()
        raise


def set_default_resume(
    db: Session,
    user_id: UUID,
    resume_id: UUID,
) -> Resume | None:
    """Set one resume as the user's default resume."""

    resume = get_resume_by_id(db, user_id, resume_id)

    if resume is None:
        return None

    try:
        user_resumes = db.scalars(
            select(Resume).where(
                Resume.user_id == user_id
            )
        ).all()

        for item in user_resumes:
            item.is_default = item.id == resume_id

        db.commit()
        db.refresh(resume)

        return resume

    except Exception:
        db.rollback()
        raise
