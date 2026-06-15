import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from typing import List
from models import MatchRequest, MatchResponse, MatchResult
from matcher import calculate_similarity_and_match
from parser import extract_text_from_file

app = FastAPI(
    title="Smart Resume Screening API",
    description="API for matching resumes against a Job Description using blazing-fast Groq and parallel processing.",
    version="1.0.0"
)

def process_single_resume_sync(job_description: str, resume_id: str, resume_text: str):
    """Synchronous worker function to process a single resume."""
    if not resume_text.strip():
        raise Exception("Could not extract any text from the file.")
        
    match_data = calculate_similarity_and_match(job_description, resume_text)
    
    return MatchResult(
        resume_id=resume_id,
        match_score=match_data["match_score"],
        matched_skills=match_data["matched_skills"],
        missing_skills=match_data["missing_skills"],
        extracted_skills=match_data["extracted_skills"],
        total_experience=match_data["total_experience"],
        explanation=match_data["explanation"]
    )

async def process_file_concurrently(job_description: str, file: UploadFile):
    """Parses and matches a file asynchronously by offloading to a thread pool."""
    try:
        file_bytes = await file.read()
        # Parse the file in a separate thread so it doesn't block the async loop
        resume_text = await asyncio.to_thread(extract_text_from_file, file_bytes, file.filename)
        # Call the LLM API in a separate thread so it doesn't block
        result = await asyncio.to_thread(process_single_resume_sync, job_description, file.filename, resume_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")

@app.post("/match", response_model=MatchResponse)
async def match_resumes(request: MatchRequest):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    if not request.resumes:
        raise HTTPException(status_code=400, detail="At least one resume must be provided.")
        
    # Process all resumes concurrently
    tasks = []
    for resume in request.resumes:
        tasks.append(
            asyncio.to_thread(process_single_resume_sync, request.job_description, resume.id, resume.text)
        )
    
    # Wait for all tasks to finish concurrently
    try:
        results = await asyncio.gather(*tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return MatchResponse(results=results)

@app.post("/match_files", response_model=MatchResponse)
async def match_files(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    if not files:
        raise HTTPException(status_code=400, detail="At least one file must be provided.")
        
    # Process all uploaded files concurrently
    tasks = [process_file_concurrently(job_description, file) for file in files]
    
    results = await asyncio.gather(*tasks)
            
    return MatchResponse(results=results)
