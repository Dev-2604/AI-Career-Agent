
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from fastapi import HTTPException, status


def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF resume."""

    try:
        reader = PdfReader(file_path)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password-protected PDF files are not supported.",
            )

        extracted_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            extracted_text.append(page_text)

        return "\n".join(extracted_text).strip()

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the uploaded PDF file.",
        )


def extract_docx_text(file_path: str) -> str:
    """Extract text from a DOCX resume."""

    try:
        document = Document(file_path)

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        table_text = []

        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if cells:
                    table_text.append(" | ".join(cells))

        return "\n".join(paragraphs + table_text).strip()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the uploaded DOCX file.",
        )


def extract_resume_text(file_path: str) -> str:
    """Extract text based on the resume file extension."""

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported resume format.",
    )
