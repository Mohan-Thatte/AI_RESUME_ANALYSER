from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import io
from pypdf import PdfReader

from app.services.matching_service import match_resume, MatchingServiceError

router = APIRouter()

from typing import List

class SkillBreakdown(BaseModel):
    skills: int
    experience: int
    education: int
    projects: int

class Evidence(BaseModel):
    skill: str
    found_in: str

class PartialSkill(BaseModel):
    skill: str
    evidence: str

class MatchResponse(BaseModel):
    score: int
    skill_breakdown: SkillBreakdown
    evidence: List[Evidence]
    partial_skills: List[PartialSkill]
    missing_skills: List[str]
    improvement_path: List[str]
    recruiter_decision: str

@router.post("/match", response_model=MatchResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Read PDF file
    try:
        content = await resume.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
        
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    # Call matching service - let failures surface as real errors,
    # never fall back to fixed/mock data.
    try:
        result = match_resume(resume_text, job_description)
    except MatchingServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result
