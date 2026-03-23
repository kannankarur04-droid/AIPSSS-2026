import streamlit as st
from google import genai
import time

# 🔑 API setup
client = genai.Client(api_key="YOUR_API_KEY")

# 🎨 Page config
st.set_page_config(page_title="AIPSSS", layout="wide")
st.title("🎓 AI Powered Student Support System")

# ⚡ Info
st.info("⚡ Fast Mode: Common questions answered instantly | Free version")

# 🧠 Short prompt
SYSTEM_PROMPT = "Explain simply with example. Add 2 MCQs."

# 💾 Session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 💾 Cache
if "cache" not in st.session_state:
    st.session_state.cache = {}

# 📚 Offline answers (IMPORTANT 🔥)
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data and performs tasks.",
    "what is ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
    "what is python": "Python is a programming language used for web, AI, and data science.",
    "what is ram": "RAM is temporary memory used by a computer to store data for quick access.",
    "what is cpu": "CPU is the brain of the computer that processes instructions.",
    "what is internet": "The Internet is a global network that connects computers worldwide."
}

# 📜 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ User input
prompt = st.chat_input("Ask your educational doubt...")

# 🔥 LIMIT CONTROL
if prompt and len(prompt) > 200:
    st.warning("⚠️ Please ask short question (max 200 characters)")
    st.stop()

# 🔁 API function
def get_ai_response(user_prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=SYSTEM_PROMPT + "\n\nQ: " + user_prompt
        )
        return response.text if response.text else "No response."
    except Exception:
        return "⚠️ Free limit reached"

# 🚀 MAIN LOGIC
if prompt:

    user_q = prompt.lower().strip()

    # 👤 Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 💾 Cache check
    if user_q in st.session_state.cache:
        reply = st.session_state.cache[user_q]

    # ⚡ Offline DB
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # 🤖 API call
    else:
        time.sleep(4)  # ⏱ delay
        with st.spinner("Thinking..."):
            reply = get_ai_response(prompt)

    # 🔄 Fallback
    if "⚠️" in reply:
        reply = "Basic answer: " + OFFLINE_DB.get(user_q, "Please try again after some time.")

    # 💾 Save cache
    st.session_state.cache[user_q] = reply

    # 🤖 Show AI response
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
