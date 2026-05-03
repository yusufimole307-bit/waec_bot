import streamlit as st
from groq import Groq

st.set_page_config(page_title="WAEC Bot NG", page_icon="📚")
st.title("📚 WAEC Bot - Pass with Distinction")
st.caption("WAEC SSCE, GCE & NECO Tutor")

api_key = st.text_input("Enter your Groq API Key", type="password", placeholder="gsk_...")

if api_key:
    client = Groq(api_key=api_key)
    
    subject = st.selectbox("Select WAEC Subject", [
        "Mathematics", "English Language", "Biology", 
        "Physics", "Chemistry", "Economics", "Government",
        "Literature in English"
    ])
    
    question = st.text_area(
        f"Ask your {subject} question:", 
        placeholder="Example: Explain mitosis and give 2 WAEC past questions",
        height=120
    )
    
    if st.button("Get WAEC Answer", type="primary"):
        if question.strip():
            with st.spinner("WAEC Bot is preparing your answer..."):
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system", 
                                "content": """You are WAEC Bot, a professional tutor for Nigerian secondary school students. 
                                Rules:
                                1. Use clear, formal, grammatically correct English only. No slang or Pidgin.
                                2. Explain step-by-step for WAEC standard.
                                3. After explanation, provide 2 relevant WAEC past questions with detailed solutions.
                                4. Use Nigerian context/examples where helpful.
                                5. Format with headings, bullet points, and proper spacing.
                                6. Be encouraging. Align with current WAEC syllabus."""
                            },
                            {"role": "user", "content": f"Subject: {subject}. Question: {question}"}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.3,
                    )
                    st.markdown("### Answer")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: Check your API key or internet. Details: {e}")
        else:
            st.warning("Please type your question first.")
else:
    st.info("👆 Get your free API key at https://console.groq.com/keys")
    st.markdown("**Note:** Revoke any key you exposed before.")
