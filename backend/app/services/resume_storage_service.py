
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def get_user_resume_directory(user_id: uuid.UUID) -> Path:
    """Return the private storage directory for a user."""

    storage_root = Path(settings.RESUME_STORAGE_DIR).resolve()
    user_directory = (storage_root / str(user_id)).resolve()

    # Ensure the resolved directory stays inside the storage root.
    if not user_directory.is_relative_to(storage_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid storage location.",
        )

    user_directory.mkdir(parents=True, exist_ok=True)

    return user_directory


async def save_resume_file(
    user_id: uuid.UUID,
    file: UploadFile,
) -> dict:
    """Validate and securely save a resume file."""

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    if extension not in settings.ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are allowed.",
        )

    max_size = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    content = await file.read(max_size + 1)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size cannot exceed {settings.MAX_RESUME_SIZE_MB} MB.",
        )

    # Basic file-signature validation.
    if extension == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file.",
        )

    if extension == ".docx" and not content.startswith(b"PK"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid DOCX file.",
        )

    user_directory = get_user_resume_directory(user_id)

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = user_directory / stored_filename

    try:
        file_path.write_bytes(content)
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store uploaded resume.",
        )

    return {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "file_extension": extension,
    }


def delete_resume_file(file_path: str) -> None:
    """Delete a stored resume file if it exists."""

    path = Path(file_path).resolve()
    storage_root = Path(settings.RESUME_STORAGE_DIR).resolve()

    if not path.is_relative_to(storage_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume storage path.",
        )

    if path.exists() and path.is_file():
        path.unlink()
