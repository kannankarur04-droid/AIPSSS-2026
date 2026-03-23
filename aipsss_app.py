import streamlit as st
from google import genai
import time
import re

if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS Expert", layout="wide", page_icon="🎓")
st.title("🎓 AI Student Support System (Expert Mode)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your educational doubt...")

SYSTEM_PROMPT = """You are a professional teacher. 
Explain concepts in detail with 5 bullet points and a simple example. 
Use LaTeX for math formulas. 
At the end, add 2 Multiple Choice Questions (MCQs) for the student to practice."""

def extract_math(q):
    match = re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q)
    return match.group() if match else None

def get_ai_response(q):
    try:
        # gemini-2.0-flash மாடலைப் பயன்படுத்துகிறது
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=SYSTEM_PROMPT + "\n\nQuestion: " + q
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

if prompt:
    user_q = prompt.lower().strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    math_expr = extract_math(user_q)
    
    with st.chat_message("assistant"):
        if math_expr:
            try:
                result = eval(math_expr)
                reply = f"**Calculation Result:** {math_expr} = {result}"
            except:
                reply = get_ai_response(prompt)
        else:
            with st.spinner("Thinking like a teacher..."):
                reply = get_ai_response(prompt)
        
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
