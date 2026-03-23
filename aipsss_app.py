import streamlit as st
from google import genai
import time
import re

# 🔑 API (use secrets in production)
client = genai.Client(api_key="YOUR_API_KEY")

# 🎨 UI
st.set_page_config(page_title="AIPSSS", layout="wide")
st.title("🎓 AI Student Support System")

# 💾 Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📚 Offline DB (basic but useful)
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data and performs tasks.",
    "what is mcq": "MCQ (Multiple Choice Question) is a type of question where you choose the correct answer from options.",
    "what is ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
    "what is electronics": "Electronics is the study of circuits and electronic devices like transistors and microchips.",
    "what is commerce": "Commerce is the activity of buying and selling goods and services.",
    "what is science": "Science is the study of the natural world.",
}

# 📜 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input
prompt = st.chat_input("Ask your question...")

# ➕ Extract math expression
def extract_math(q):
    match = re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q)
    if match:
        return match.group()
    return None

# 🤖 AI response
def get_ai_response(q):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Explain simply with example:\n\n" + q
        )
        return response.text
    except:
        return None

# 🚀 MAIN
if prompt:

    user_q = prompt.lower().strip()

    # 👤 show user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None

    # ✅ 1. Math (priority)
    math_expr = extract_math(user_q)
    if math_expr:
        try:
            reply = f"Answer: {eval(math_expr)}"
        except:
            reply = None

    # ✅ 2. Offline answers
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # ✅ 3. AI (Gemini)
    else:
        with st.spinner("Thinking..."):
            time.sleep(2)
            reply = get_ai_response(prompt)

    # ✅ 4. Fallback
    if not reply:
        reply = "⚠️ Server busy. Please try again in a few seconds."

    # 🤖 show reply
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
