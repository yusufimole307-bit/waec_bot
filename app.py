import json
import re
import time
from datetime import datetime

import streamlit as st
from groq import Groq


# ============================================================
# WAEC BOT NG — PROFESSIONAL EDITION
# ============================================================
# AI-powered learning platform
#
# FEATURES
# - AI Tutor
# - Teach Me
# - Hint Mode
# - Practice Quiz
# - Mock Exam
# - XP / Levels
# - Accuracy tracking
# - Study streak
# - Multiple subjects
# - Multiple languages
# - Professional responsive UI
#
# PAYMENT SYSTEM: NOT INCLUDED
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "WAEC Bot NG"
MODEL_NAME = "llama-3.3-70b-versatile"


st.set_page_config(
    page_title=f"{APP_NAME} | AI Study Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at 5% 0%,
            rgba(37, 99, 235, 0.16),
            transparent 27%
        ),
        radial-gradient(
            circle at 95% 0%,
            rgba(124, 58, 237, 0.14),
            transparent 27%
        ),
        #07111f;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

section[data-testid="stSidebar"] {
    background: #050b14;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.hero {
    padding: 34px;
    border-radius: 26px;
    background:
        linear-gradient(
            135deg,
            rgba(37,99,235,0.22),
            rgba(124,58,237,0.18)
        );
    border: 1px solid rgba(255,255,255,0.09);
    margin-bottom: 24px;
}

.hero h1 {
    margin: 0;
    color: white;
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 900;
}

.hero p {
    color: #b9c7d9;
    font-size: 17px;
    margin: 8px 0 0;
}

.card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 20px;
    min-height: 135px;
}

.card h3 {
    color: white;
    margin: 7px 0;
}

.card p {
    color: #9fb0c4;
    margin: 0;
}

.badge {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(37,99,235,0.16);
    border: 1px solid rgba(96,165,250,0.25);
    color: #cfe1ff;
    font-size: 13px;
}

.small {
    color: #91a4ba;
    font-size: 13px;
}

.stButton > button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 750;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 13px;
}

div[data-testid="stChatMessage"] {
    border-radius: 15px;
}

.stTextInput input,
.stTextArea textarea {
    border-radius: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SUBJECTS
# ============================================================

SUBJECTS = [
    "Auto Detect / Any Subject",
    "Mathematics",
    "Further Mathematics",
    "English Language",
    "Literature in English",
    "Biology",
    "Chemistry",
    "Physics",
    "Agricultural Science",
    "Economics",
    "Government",
    "Geography",
    "Civic Education",
    "Christian Religious Studies",
    "Islamic Religious Studies",
    "Commerce",
    "Accounting",
    "Business Studies",
    "Computer Science",
    "Data Processing",
    "Information Technology",
    "Home Economics",
    "Food and Nutrition",
    "Technical Drawing",
    "Basic Technology",
    "Health Education",
    "Physical Education",
    "Visual Arts",
    "Music",
    "Arabic",
    "French",
    "Yoruba",
    "Hausa",
    "Igbo",
    "Spanish",
    "German",
    "Portuguese",
    "Programming",
    "Web Development",
    "Database Systems",
    "Artificial Intelligence",
    "Machine Learning",
    "Cybersecurity",
    "Statistics",
    "Calculus",
    "Linear Algebra",
    "General Knowledge",
    "Custom Subject",
]


# ============================================================
# ACADEMIC LEVELS
# ============================================================

LEVELS = [
    "Primary School",
    "Junior Secondary School",
    "Senior Secondary School",
    "WAEC / NECO",
    "JAMB / UTME",
    "University",
    "Professional",
    "General Knowledge",
]


# ============================================================
# LANGUAGES
# ============================================================

LANGUAGES = [
    "English",
    "العربية — Arabic",
    "Français — French",
    "Español — Spanish",
    "Português — Portuguese",
    "Deutsch — German",
    "中文 — Chinese",
    "हिन्दी — Hindi",
    "Yorùbá",
    "Hausa",
    "Igbo",
    "Swahili",
    "Türkçe — Turkish",
    "Italiano — Italian",
]


# ============================================================
# LEARNING MODES
# ============================================================

MODES = [
    "🤖 AI Tutor",
    "🧠 Teach Me",
    "🎯 Practice Quiz",
    "📝 Mock Exam",
    "💡 Hint",
]


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session():

    defaults = {

        "messages": [],

        "mode": "🤖 AI Tutor",

        "subject": "Auto Detect / Any Subject",

        "custom_subject": "",

        "level_name": "WAEC / NECO",

        "language": "English",

        "xp": 0,

        "questions_answered": 0,

        "correct_answers": 0,

        "streak": 1,

        "daily_date": str(datetime.now().date()),

        "quiz": None,

        "quiz_answers": {},

        "quiz_submitted": False,

        "quiz_score": 0,

        "exam": None,

        "exam_answers": {},

        "exam_submitted": False,

        "exam_score": 0,

        "exam_started": None,

        "last_request": 0.0,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_session()


# ============================================================
# GROQ CONNECTION
# ============================================================

def get_groq_client():

    try:

        api_key = st.secrets.get(
            "GROQ_API_KEY",
            ""
        )

        if not api_key:

            return None

        return Groq(
            api_key=api_key
        )

    except Exception:

        return None


client = get_groq_client()


# ============================================================
# CURRENT SUBJECT
# ============================================================

def get_current_subject():

    if st.session_state.subject == "Custom Subject":

        custom_subject = (
            st.session_state.custom_subject.strip()
        )

        if custom_subject:

            return custom_subject

        return "General Knowledge"

    return st.session_state.subject


# ============================================================
# XP SYSTEM
# ============================================================

def add_xp(amount):

    amount = max(
        0,
        int(amount)
    )

    st.session_state.xp += amount


def get_level():

    return (
        st.session_state.xp // 100
    ) + 1


# ============================================================
# ACCURACY
# ============================================================

def get_accuracy():

    total = (
        st.session_state.questions_answered
    )

    if total <= 0:

        return 0.0

    return (
        st.session_state.correct_answers
        / total
    ) * 100


# ============================================================
# SIMPLE REQUEST PROTECTION
# ============================================================

def request_allowed():

    now = time.time()

    last_request = (
        st.session_state.last_request
    )

    if now - last_request < 1.2:

        return False

    st.session_state.last_request = now

    return True


# ============================================================
# CLEAN AI JSON
# ============================================================

def clean_json(text):

    if not text:

        return ""

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt():

    subject = get_current_subject()

    level = st.session_state.level_name

    language = st.session_state.language

    mode = st.session_state.mode

    return f"""
You are {APP_NAME}, a professional AI educational assistant.

Current subject:
{subject}

Academic level:
{level}

Learning mode:
{mode}

Response language:
{language}

Your responsibilities:

1. Teach clearly and accurately.
2. Match the student's academic level.
3. Break difficult topics into simple steps.
4. Use examples when helpful.
5. For mathematics and science calculations,
   show formulas and working.
6. Correct mistakes politely.
7. Encourage students without making false promises.
8. Never fabricate official WAEC results.
9. Never claim an AI-generated question is an
   authentic WAEC, NECO or JAMB past question.
10. Clearly label generated questions as practice
    or WAEC-style practice when appropriate.
11. Never invent sources.
12. Keep answers organized and easy to read.
13. If the student asks something outside the
    selected subject, still help if appropriate.
14. Prioritize educational value over unnecessary
    verbosity.
"""


# ============================================================
# ASK AI
# ============================================================

def ask_ai(
    prompt,
    history=None,
    temperature=0.25,
    max_tokens=3500
):

    if client is None:

        return """
⚠️ **AI service is not connected yet.**

The app owner needs to add the Groq API key to
Streamlit Secrets.

Use:

```toml
GROQ_API_KEY = "your_api_key_here"
