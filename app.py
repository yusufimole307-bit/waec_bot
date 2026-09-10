import json
import random
import time

import streamlit as st
from groq import Groq


# =========================================================
# APP SETTINGS
# =========================================================

APP_NAME = "WAEC Bot NG"

# Current Groq model
MODEL_NAME = "openai/gpt-oss-120b"

SUBJECTS = [
    "English Language",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "Government",
    "Literature in English",
    "Geography",
    "Agricultural Science",
    "Commerce",
    "Accounting",
    "Computer Studies",
    "Civic Education",
    "Christian Religious Studies",
    "Islamic Religious Studies",
]

LEVELS = [
    "SS1",
    "SS2",
    "SS3",
    "WAEC",
    "JAMB",
]

LANGUAGES = [
    "English",
    "Simple English",
]


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .hero {
        background: linear-gradient(135deg, #111827, #1f2937);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 20px;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 18px;
        color: #d1d5db;
    }

    .card {
        background: #111827;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #374151;
        margin-bottom: 15px;
    }

    .xp {
        font-size: 22px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "messages": [],
    "mode": "AI Tutor",
    "subject": "Mathematics",
    "custom_subject": "",
    "level": "WAEC",
    "language": "English",

    "xp": 0,
    "questions_answered": 0,
    "correct_answers": 0,

    "quiz_questions": [],
    "quiz_index": 0,
    "quiz_score": 0,

    "exam_questions": [],
    "exam_index": 0,
    "exam_score": 0,
    "exam_started": False,
    "exam_start_time": 0.0,
}


for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# GROQ API KEY
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"].strip()
except Exception:
    GROQ_API_KEY = ""


client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as error:
        st.error(f"Could not create Groq client: {error}")
        client = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_selected_subject():
    if st.session_state.subject == "Other":
        custom = st.session_state.custom_subject.strip()

        if custom:
            return custom

        return "General"

    return st.session_state.subject


def add_xp(amount):
    st.session_state.xp += amount


def record_answer(correct):
    st.session_state.questions_answered += 1

    if correct:
        st.session_state.correct_answers += 1
        add_xp(10)
    else:
        add_xp(2)


def get_accuracy():
    total = st.session_state.questions_answered

    if total == 0:
        return 0

    return round(
        (st.session_state.correct_answers / total) * 100,
        1
    )


# =========================================================
# AI SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = (
    "You are WAEC Bot NG, a friendly Nigerian secondary "
    "school education assistant. "

    "Help students prepare for WAEC, NECO and JAMB. "

    "Explain answers clearly and step by step. "

    "Use Nigerian school terminology where appropriate. "

    "Do not claim that generated questions are leaked "
    "or real examination questions. "

    "If a question is difficult, break it into simple steps. "

    "For mathematics and science, show calculations. "

    "For English, explain grammar and vocabulary clearly. "

    "For essay questions, provide useful structure and examples. "

    "Encourage learning rather than cheating."
)


# =========================================================
# ASK AI
# =========================================================

def ask_ai(user_message):

    if not GROQ_API_KEY:
        return (
            "⚠️ **Groq API key is not connected.**\n\n"
            "Please add `GROQ_API_KEY` to your Streamlit Secrets."
        )

    if client is None:
        return (
            "⚠️ **Groq client could not be created.**\n\n"
            "Please check your API key."
        )

    try:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        for message in st.session_state.messages[-10:]:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.4,
            max_tokens=1800,
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "❌ **Groq API error**\n\n"
            f"`{type(error).__name__}: {error}`"
        )


# =========================================================
# GENERATE QUESTIONS
# =========================================================

def generate_questions(count=5):

    subject = get_selected_subject()
    level = st.session_state.level

    if not GROQ_API_KEY:
        st.error(
            "❌ GROQ_API_KEY was not found in Streamlit Secrets."
        )
        return []

    if client is None:
        st.error(
            "❌ Groq client could not be created."
        )
        return []

    prompt = (
        f"Create {count} multiple-choice practice questions "
        f"for {subject} at {level} level.\n\n"

        "Return ONLY valid JSON.\n\n"

        "Use exactly this structure:\n"

        "[\n"
        "  {\n"
        '    "question": "Question here",\n'
        '    "options": [\n'
        '      "Option A",\n'
        '      "Option B",\n'
        '      "Option C",\n'
        '      "Option D"\n'
        "    ],\n"
        '    "answer": "The exact correct option",\n'
        '    "explanation": "Short explanation"\n'
        "  }\n"
        "]\n\n"

        "Rules:\n"
        "- Exactly four options per question.\n"
        "- Exactly one correct answer.\n"
        "- The answer must exactly match one option.\n"
        "- No markdown.\n"
        "- Do not use ```json.\n"
        "- Return JSON only."
    )

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a WAEC question generator. "
                        "Return valid JSON only."
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

        raw = response.choices[0].message.content

        if not raw:
            st.error(
                "❌ Groq returned an empty response."
            )
            return []

        raw = raw.strip()

        with st.expander("🔧 Developer Debug"):
            st.code(raw)

        # Remove markdown code fences if the AI accidentally adds them
        if raw.startswith("```"):
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

        data = json.loads(raw)

        if not isinstance(data, list):
            st.error(
                "❌ Groq returned JSON, but it was not a list."
            )
            return []

        cleaned = []

        for item in data:

            if not isinstance(item, dict):
                continue

            question = item.get("question")
            options = item.get("options")
            answer = item.get("answer")
            explanation = item.get(
                "explanation",
                ""
            )

            if not question:
                continue

            if not isinstance(options, list):
                continue

            if len(options) != 4:
                continue

            if not answer:
                continue

            if answer not in options:
                continue

            cleaned.append(
                {
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation,
                }
            )

        if not cleaned:
            st.error(
                "❌ Groq responded, but none of the questions passed validation."
            )
            return []

        return cleaned

    except json.JSONDecodeError as error:

        st.error(
            "❌ Groq returned invalid JSON."
        )

        st.code(
            f"JSON error: {error}"
        )

        return []

    except Exception as error:

        st.error(
            "❌ Groq API error:"
        )

        st.code(
            f"{type(error).__name__}: {error}"
        )

        return []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🎓 WAEC Bot NG")

    mode_options = [
        "AI Tutor",
        "Teach Me",
        "Practice Quiz",
        "Mock Exam",
    ]

    st.session_state.mode = st.selectbox(
        "Choose Mode",
        mode_options,
        index=mode_options.index(
            st.session_state.mode
        ),
    )

    st.markdown("---")

    subject_options = SUBJECTS + ["Other"]

    st.session_state.subject = st.selectbox(
        "📚 Subject",
        subject_options,
        index=subject_options.index(
            st.session_state.subject
        ),
    )

    if st.session_state.subject == "Other":

        st.session_state.custom_subject = st.text_input(
            "Enter subject",
            value=st.session_state.custom_subject,
        )

    st.session_state.level = st.selectbox(
        "🎯 Level",
        LEVELS,
        index=LEVELS.index(
            st.session_state.level
        ),
    )

    st.session_state.language = st.selectbox(
        "🌍 Language",
        LANGUAGES,
        index=LANGUAGES.index(
            st.session_state.language
        ),
    )

    st.markdown("---")

    st.markdown(
        f"<div class='xp'>⭐ XP: "
        f"{st.session_state.xp}</div>",
        unsafe_allow_html=True,
    )

    st.write(
        "Questions answered: "
        + str(st.session_state.questions_answered)
    )

    st.write(
        "Correct answers: "
        + str(st.session_state.correct_answers)
    )

    st.write(
        "Accuracy: "
        + str(get_accuracy())
        + "%"
    )

    st.markdown("---")

    if st.button(
        "🔄 Reset Progress",
        use_container_width=True
    ):

        st.session_state.xp = 0
        st.session_state.questions_answered = 0
        st.session_state.correct_answers = 0

        st.session_state.quiz_questions = []
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0

        st.session_state.exam_questions = []
        st.session_state.exam_index = 0
        st.session_state.exam_score = 0

        st.session_state.messages = []

        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class='hero'>
        <h1>🎓 WAEC Bot NG</h1>
        <p>
            Your AI-powered study assistant for WAEC,
            NECO and JAMB.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DASHBOARD METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "⭐ XP",
        st.session_state.xp
    )

with col2:
    st.metric(
        "✅ Correct",
        st.session_state.correct_answers
    )

with col3:
    st.metric(
        "📊 Accuracy",
        f"{get_accuracy()}%"
    )


st.markdown("---")


# =========================================================
# AI TUTOR
# =========================================================

if st.session_state.mode == "AI Tutor":

    st.subheader("🤖 AI Tutor")

    st.write(
        f"Subject: **{get_selected_subject()}**"
    )

    st.write(
        f"Level: **{st.session_state.level}**"
    )

    if not GROQ_API_KEY:

        st.warning(
            "⚠️ Groq is not connected. "
            "Add GROQ_API_KEY to Streamlit Secrets."
        )

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    user_input = st.chat_input(
        "Ask me anything about your subject..."
    )

    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                answer = ask_ai(
                    user_input
                )

            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# =========================================================
# TEACH ME
# =========================================================

elif st.session_state.mode == "Teach Me":

    st.subheader("👨‍🏫 Teach Me")

    topic = st.text_input(
        "What topic do you want me to teach you?"
    )

    difficulty = st.select_slider(
        "Difficulty",
        options=[
            "Beginner",
            "Intermediate",
            "Advanced"
        ],
        value="Intermediate",
    )

    if st.button(
        "📖 Teach Me",
        use_container_width=True
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic."
            )

        else:

            prompt = (
                f"Teach me the topic '{topic}' "
                f"for {get_selected_subject()} "
                f"at {st.session_state.level} level. "

                f"Difficulty: {difficulty}. "

                "Explain it step by step using simple language. "
                "Include examples and finish with three short questions."
            )

            with st.spinner(
                "Preparing your lesson..."
            ):

                answer = ask_ai(prompt)

            st.markdown(
                "<div class='card'>",
                unsafe_allow_html=True,
            )

            st.markdown(answer)

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            add_xp(5)


# =========================================================
# PRACTICE QUIZ
# =========================================================

elif st.session_state.mode == "Practice Quiz":

    st.subheader("📝 Practice Quiz")

    if not st.session_state.quiz_questions:

        st.write(
            "Generate a practice quiz based on "
            "your selected subject and level."
        )

        number = st.slider(
            "Number of questions",
            min_value=3,
            max_value=10,
            value=5,
        )

        if st.button(
            "🚀 Start Quiz",
            use_container_width=True
        ):

            with st.spinner(
                "Generating questions..."
            ):

                questions = generate_questions(
                    number
                )

            if questions:

                random.shuffle(
                    questions
                )

                st.session_state.quiz_questions = questions
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0

                st.rerun()

            else:

                st.error(
                    "I couldn't generate the quiz."
                )

    else:

        questions = st.session_state.quiz_questions
        index = st.session_state.quiz_index

        if index < len(questions):

            question = questions[index]

            st.progress(
                (index + 1) / len(questions)
            )

            st.markdown(
                f"### Question {index + 1} "
                f"of {len(questions)}"
            )

            st.write(
                question["question"]
            )

            selected = st.radio(
                "Choose your answer:",
                question["options"],
                key=f"quiz_answer_{index}",
            )

            if st.button(
                "Submit Answer",
                use_container_width=True
            ):

                correct = (
                    selected
                    == question["answer"]
                )

                record_answer(
                    correct
                )

                if correct:

                    st.success(
                        "🎉 Correct! +10 XP"
                    )

                    st.session_state.quiz_score += 1

                else:

                    st.error(
                        "❌ Incorrect. "
                        f"Correct answer: "
                        f"{question['answer']}"
                    )

                if question["explanation"]:

                    st.info(
                        "💡 Explanation: "
                        + question["explanation"]
                    )

                st.session_state.quiz_index += 1

                time.sleep(0.5)

                st.rerun()

        else:

            score = st.session_state.quiz_score
            total = len(questions)

            percentage = round(
                (score / total) * 100,
                1
            )

            st.success(
                "🎉 Quiz Completed!"
            )

            st.metric(
                "Your Score",
                f"{score}/{total}"
            )

            st.write(
                f"Percentage: **{percentage}%**"
            )

            if percentage >= 80:

                st.balloons()

                st.success(
                    "🔥 Excellent performance!"
                )

            elif percentage >= 60:

                st.info(
                    "👍 Good job. Keep practising."
                )

            else:

                st.warning(
                    "📚 Keep studying and try again."
                )

            if st.button(
                "🔄 New Quiz",
                use_container_width=True
            ):

                st.session_state.quiz_questions = []
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0

                st.rerun()


# =========================================================
# MOCK EXAM
# =========================================================

elif st.session_state.mode == "Mock Exam":

    st.subheader("🎯 WAEC-Style Mock Exam")

    if not st.session_state.exam_questions:

        st.write(
            "Take a timed AI-generated mock examination."
        )

        number = st.slider(
            "Number of questions",
            min_value=5,
            max_value=20,
            value=10,
        )

        if st.button(
            "🚀 Start Mock Exam",
            use_container_width=True
        ):

            with st.spinner(
                "Generating your examination..."
            ):

                questions = generate_questions(
                    number
                )

            if questions:

                random.shuffle(
                    questions
                )

                st.session_state.exam_questions = questions
                st.session_state.exam_index = 0
                st.session_state.exam_score = 0
                st.session_state.exam_started = True
                st.session_state.exam_start_time = time.time()

                st.rerun()

            else:

                st.error(
                    "Unable to generate the examination."
                )

    else:

        questions = st.session_state.exam_questions
        index = st.session_state.exam_index

        if index < len(questions):

            elapsed = (
                time.time()
                - st.session_state.exam_start_time
            )

            total_seconds = (
                len(questions) * 60
            )

            remaining = max(
                0,
                total_seconds
                - int(elapsed)
            )

            minutes = remaining // 60
            seconds = remaining % 60

            st.info(
                f"⏱️ Time remaining: "
                f"{minutes:02d}:{seconds:02d}"
            )

            st.progress(
                (index + 1) / len(questions)
            )

            question = questions[index]

            st.markdown(
                f"### Question {index + 1} "
                f"of {len(questions)}"
            )

            st.write(
                question["question"]
            )

            selected = st.radio(
                "Select an answer:",
                question["options"],
                key=f"exam_answer_{index}",
            )

            if st.button(
                "Next Question",
                use_container_width=True
            ):

                correct = (
                    selected
                    == question["answer"]
                )

                record_answer(
                    correct
                )

                if correct:

                    st.session_state.exam_score += 1

                st.session_state.exam_index += 1

                st.rerun()

            if remaining <= 0:

                st.session_state.exam_index = len(
                    questions
                )

                st.rerun()

        else:

            score = st.session_state.exam_score
            total = len(questions)

            percentage = round(
                (score / total) * 100,
                1
            )

            st.success(
                "🏁 Mock Examination Completed!"
            )

            st.metric(
                "Final Score",
                f"{score}/{total}"
            )

            st.metric(
                "Percentage",
                f"{percentage}%"
            )

            if percentage >= 75:

                st.balloons()

                st.success(
                    "🔥 Excellent! You are doing well."
                )

            elif percentage >= 50:

                st.info(
                    "👍 Fair performance. "
                    "More practice will help."
                )

            else:

                st.warning(
                    "📚 Keep studying. "
                    "You can improve!"
                )

            if st.button(
                "🔄 Take Another Exam",
                use_container_width=True
            ):

                st.session_state.exam_questions = []
                st.session_state.exam_index = 0
                st.session_state.exam_score = 0
                st.session_state.exam_started = False
                st.session_state.exam_start_time = 0.0

                st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style='text-align:center;color:#9ca3af;'>
        🎓 WAEC Bot NG • Built for Nigerian Students
        <br>
        Study smart. Practise more. Succeed.
    </div>
    """,
    unsafe_allow_html=True,
)
