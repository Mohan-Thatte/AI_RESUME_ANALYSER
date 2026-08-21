from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os

from app.services.resume_parser import extract_text_from_pdf

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(contents)
        temp_path = temp.name

    try:
        text = extract_text_from_pdf(temp_path)

        return {
            "filename": file.filename,
            "text": text
        }

    finally:
        os.remove(temp_path)