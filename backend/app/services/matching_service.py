import os
import json
from groq import Groq
from typing import Dict, Any


# Groq deprecated its Llama chat models (llama-3.3-70b-versatile,
# llama-3.1-8b-instant) in June 2026. openai/gpt-oss-120b is their
# recommended replacement for general-purpose / reasoning workloads
# and supports JSON mode.
MODEL_NAME = "openai/gpt-oss-120b"

SCHEMA_INSTRUCTIONS = """
You are an expert technical recruiter and ATS algorithm.
Analyze the resume against the job description and respond ONLY with a
JSON object matching exactly this schema (no extra commentary, no markdown fences):

{
    "score": (integer 0-100, AI semantic match percentage),
    "skill_breakdown": {
        "skills": (integer 0-100),
        "experience": (integer 0-100),
        "education": (integer 0-100),
        "projects": (integer 0-100)
    },
    "evidence": [
        array of objects representing matched skills and where they were found, e.g.:
        {"skill": "Python", "found_in": "Skills section or Project 1"}
    ],
    "partial_skills": [
        array of objects for skills partially met, e.g.:
        {"skill": "Docker", "evidence": "Mentioned in coursework but no applied experience"}
    ],
    "missing_skills": [array of strings for skills entirely missing],
    "improvement_path": [array of 3-4 actionable tips to reach a 90%+ match],
    "recruiter_decision": (string, must be exactly one of: "Strong Shortlist", "Consider", "Not Recommended")
}
"""


class MatchingServiceError(Exception):
    """Raised when the AI matching service cannot produce a real result.

    Callers must surface this as an error to the client rather than
    substituting static/fallback data.
    """
    pass


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MatchingServiceError(
            "GROQ_API_KEY is not configured on the backend. "
            "Set it in backend/.env to enable resume analysis."
        )
    return Groq(api_key=api_key)


def match_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    client = _get_client()

    user_prompt = f"""
    Job Description:
    {job_description}

    Resume Text:
    {resume_text}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SCHEMA_INSTRUCTIONS},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except Exception as e:
        raise MatchingServiceError(f"Groq API request failed: {e}") from e

    try:
        content = response.choices[0].message.content
        return json.loads(content)
    except (json.JSONDecodeError, AttributeError, IndexError, KeyError) as e:
        raise MatchingServiceError(
            f"Groq returned a response that could not be parsed as JSON: {e}"
        ) from e


def generate_cover_letter(resume_text: str, job_description: str) -> str:
    client = _get_client()

    prompt = f"""
    Write a professional and compelling cover letter based on the following resume and job description.
    Focus on bridging the gap between their existing skills and the job requirements. Keep it under 4 paragraphs.

    Job Description:
    {job_description}

    Resume Text:
    {resume_text}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise MatchingServiceError(f"Groq API request failed: {e}") from e
