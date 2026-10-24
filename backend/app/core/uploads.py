from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.services.resume.parser import extract_resume_data_from_bytes, extract_text_from_bytes

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def safe_original_name(filename: Optional[str]) -> str:
    name = Path(filename or "upload").name
    return name[:200] if name else "upload"


def file_extension(filename: Optional[str]) -> str:
    return Path(filename or "").suffix.lower()


async def read_allowed_upload(upload: UploadFile) -> Tuple[bytes, str, str]:
    settings = get_settings()
    original = safe_original_name(upload.filename)
    ext = file_extension(original)

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Use PDF, DOCX, or TXT.",
        )

    data = await upload.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large. Maximum size is 4 MB.",
        )
    return data, original, ext


def parse_resume_upload(data: bytes, ext: str) -> dict:
    parsed = extract_resume_data_from_bytes(data, ext)
    if parsed.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=parsed["error"],
        )
    return parsed


def extract_document_text(data: bytes, ext: str) -> str:
    text = extract_text_from_bytes(data, ext)
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the uploaded file.",
        )
    return text


def validate_jd_text(text: str) -> str:
    settings = get_settings()
    cleaned = (text or "").strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a job description as file or text.",
        )
    if len(cleaned) > settings.max_jd_chars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job description is too long. Maximum is {settings.max_jd_chars} characters.",
        )
    return cleaned
