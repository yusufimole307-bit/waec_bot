import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq


# =========================================================
# ENVIRONMENT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="HIZQEEL MULTI_TUTOR API",
    description="AI-powered education backend for WAEC, NECO and JAMB.",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class TutorRequest(BaseModel):
    message: str
    subject: str = "General"
    level: str = "Student"
    language: str = "English"


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "HIZQEEL MULTI_TUTOR API is running!",
        "status": "success",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# CONNECTION TEST
# =========================================================

@app.get("/api/test")
def test():
    return {
        "message": "Backend connection successful!"
    }


# =========================================================
# AI TUTOR
# =========================================================

@app.post("/api/tutor")
def tutor(request: TutorRequest):

    if client is None:
        return {
            "success": False,
            "error": "GROQ_API_KEY is not configured on the backend.",
        }

    system_prompt = f"""
You are HIZQEEL MULTI_TUTOR, a friendly Nigerian AI school
education assistant.

Help students learn and prepare for WAEC, NECO and JAMB.

Subject: {request.subject}
Level: {request.level}
Language: {request.language}

Explain things clearly and simply.

Show step-by-step solutions when necessary.

Give accurate educational information.

Adapt your explanation to the selected subject.

Do not claim that generated questions are leaked
or real examination questions.

Encourage learning and understanding.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": request.message,
                },
            ],
            temperature=0.4,
            max_tokens=1800,
        )

        answer = response.choices[0].message.content

        return {
            "success": True,
            "answer": answer,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# QUESTION GENERATION
# =========================================================

@app.post("/api/questions")
def questions(request: TutorRequest):

    if client is None:
        return {
            "success": False,
            "error": "GROQ_API_KEY is not configured on the backend.",
        }

    prompt = f"""
Create 5 multiple-choice practice questions.

Subject: {request.subject}
Level: {request.level}

The questions should be suitable for Nigerian students
preparing for {request.level} examinations.

Return ONLY valid JSON.

Use exactly this structure:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A",
    "explanation": "Short explanation"
  }}
]

Rules:

- Exactly 5 questions.
- Exactly 4 options per question.
- Exactly one correct answer.
- The answer must exactly match one of the options.
- Include a short explanation.
- Questions must be educational.
- Do not claim they are leaked examination questions.
- Do not include markdown.
- Do not use ```json.
- Return JSON only.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an educational multiple-choice "
                        "question generator. Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.5,
            max_tokens=3000,
        )

        raw_questions = response.choices[0].message.content

        if not raw_questions:
            return {
                "success": False,
                "error": "AI returned an empty response.",
            }

        return {
            "success": True,
            "questions": raw_questions,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }