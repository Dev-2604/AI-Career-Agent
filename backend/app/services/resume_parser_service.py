
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from fastapi import HTTPException, status


def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF resume."""

    try:
        reader = PdfReader(file_path, strict=True)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password-protected PDF files are not supported.",
            )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                extracted_pages.append(
                    f"--- Page {page_number} ---\n{page_text.strip()}"
                )

        extracted_text = "\n\n".join(extracted_pages).strip()

        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No selectable text found in this PDF. "
                    "It may be a scanned document. "
                    "Please upload a text-based PDF or DOCX."
                ),
            )

        return extracted_text

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the uploaded PDF file.",
        )


def extract_docx_text(file_path: str) -> str:
    """Extract paragraphs and table content from a DOCX resume."""

    try:
        document = Document(file_path)

        extracted_sections = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_sections.append(text)

        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if cells:
                    extracted_sections.append(" | ".join(cells))

        extracted_text = "\n".join(extracted_sections).strip()

        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text found in the DOCX resume.",
            )

        return extracted_text

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read the uploaded DOCX file.",
        )


def extract_resume_text(file_path: str) -> str:
    """Extract text according to the file extension."""

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported resume format.",
    )
