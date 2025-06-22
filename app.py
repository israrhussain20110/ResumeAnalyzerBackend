from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil

from parser import extract_text_from_docx, parse_resume
from job_parser import parse_job_description
from scorer import score_resume, generate_feedback

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Resume Analyzer API is running 🎉"}


# Enable CORS (adjust origins as needed for Flutter web or Android)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origin(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile,
    job_title: str = Form(...),
    job_description: str = Form(...),
    responsibilities: str = Form(...),
    experience: str = Form(...),
    skills: str = Form(...),
    education: str = Form(...),
):
    try:
        # Save uploaded file
        resume_path = os.path.join(UPLOAD_DIR, resume.filename)
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # Extract and parse resume
        resume_text = extract_text_from_docx(resume_path)
        resume_data = parse_resume(resume_text)

        # Parse job details
        job_data = parse_job_description(
            job_description_text=job_description,
            job_responsibilities_text=responsibilities,
            job_experience_text=experience,
            job_skills_text=skills,
            job_education_text=education
        )

        # Score and feedback
        scores = score_resume(resume_data, job_data)
        feedback = generate_feedback(resume_data, job_data)

        return {
            "score": {
                "total": float(scores["total_score"]),
                "entity": float(scores["entity_score"]),
                "skills": float(scores["skills_score"]),
                "experience": float(scores["experience_score"]),
                "education": float(scores["education_score"]),
                "structure": float(scores["structure_score"]),
            },
            "sections": scores["sections"],
            "feedback": feedback
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
