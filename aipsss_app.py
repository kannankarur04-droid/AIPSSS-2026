import streamlit as st
from google import genai
import time
import re

# 🔑 API
client = genai.Client(api_key="YOUR_API_KEY")

st.set_page_config(page_title="AIPSSS", layout="wide")
st.title("🎓 AI Student Support")

# 💾 Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📚 Simple offline DB
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data.",
    "what is mcq": "MCQ (Multiple Choice Question) is a question with options where you choose the correct answer.",
    "what is ai": "AI is intelligence shown by machines.",
}

# 📜 Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input
prompt = st.chat_input("Ask your question...")

# ➕ Math extract
def extract_math(q):
    match = re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q)
    if match:
        return match.group()
    return None

# 🤖 API
def get_ai_response(q):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=q
        )
        return response.text
    except:
        return None

# 🚀 MAIN
if prompt:

    user_q = prompt.lower().strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None

    # ✅ 1. Math (FIRST priority)
    math_expr = extract_math(user_q)
    if math_expr:
        try:
            reply = f"Answer: {eval(math_expr)}"
        except:
            reply = None

    # ✅ 2. Offline DB
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # ✅ 3. API (last)
    else:
        time.sleep(3)
        with st.spinner("Thinking..."):
            reply = get_ai_response(prompt)

    # ✅ 4. Final fallback
    if not reply:
        reply = "⚠️ Please try simple questions like '2+2' or 'what is computer'"

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
