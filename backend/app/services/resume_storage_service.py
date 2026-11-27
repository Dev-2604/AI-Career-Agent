
import io
import uuid
import zipfile
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.core.config import settings


def get_user_resume_directory(user_id: uuid.UUID) -> Path:
    """Return the private storage directory for a user."""

    storage_root = Path(settings.RESUME_STORAGE_DIR).resolve()
    user_directory = (storage_root / str(user_id)).resolve()

    if not user_directory.is_relative_to(storage_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid storage location.",
        )

    user_directory.mkdir(parents=True, exist_ok=True)

    return user_directory


def validate_pdf(content: bytes) -> None:
    """Validate the actual PDF structure."""

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file signature.",
        )

    try:
        reader = PdfReader(io.BytesIO(content), strict=True)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password-protected PDF files are not supported.",
            )

        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF contains no pages.",
            )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF is corrupted or invalid.",
        )


def validate_docx(content: bytes) -> None:
    """Validate the actual DOCX ZIP structure."""

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            if archive.testzip() is not None:
                raise ValueError("Corrupted ZIP entry.")

            required_files = {
                "[Content_Types].xml",
                "word/document.xml",
            }

            if not required_files.issubset(set(archive.namelist())):
                raise ValueError("Invalid DOCX structure.")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded DOCX is corrupted or invalid.",
        )


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

    if extension == ".pdf":
        validate_pdf(content)

    elif extension == ".docx":
        validate_docx(content)

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
