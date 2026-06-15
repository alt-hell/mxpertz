from pydantic import BaseModel
from typing import List

class Resume(BaseModel):
    id: str
    text: str

class MatchRequest(BaseModel):
    job_description: str
    resumes: List[Resume]

class MatchResult(BaseModel):
    resume_id: str
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    extracted_skills: List[str]
    total_experience: str
    explanation: str

class MatchResponse(BaseModel):
    results: List[MatchResult]
