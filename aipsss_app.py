import streamlit as st
from google import genai
import time
import re

# 🔑 API
client = genai.Client(api_key="YOUR_API_KEY")

# 🎨 UI
st.set_page_config(page_title="AIPSSS", layout="wide")
st.title("🎓 AI Powered Student Support System")
st.info("⚡ Fast Mode | Free Version | Tamil + English Supported")

# 🧠 Prompt
SYSTEM_PROMPT = "Explain simply with example. Add 2 MCQs."

# 💾 Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

# 📚 Offline DB (expanded 🔥)
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data and performs tasks.",
    "what is ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
    "what is python": "Python is a programming language used in AI, web, and data science.",
    "what is commerce": "Commerce is the activity of buying and selling goods and services.",
    "what is economics": "Economics studies how money and resources are used.",
    "what is science": "Science is the study of the natural world.",
    "what is maths": "Mathematics deals with numbers, quantities, and shapes.",
    "cpu": "CPU is the brain of the computer.",
    "ram": "RAM is temporary memory used for fast processing.",
    "internet": "Internet is a global network connecting computers."
}

# 🌐 Tamil support keywords
TAMIL_DB = {
    "கணினி": "கணினி என்பது தகவல்களை செயலாக்கும் மின்சாதனம்.",
    "ஏஐ": "ஏஐ என்பது மனித நுண்ணறிவை இயந்திரங்களில் உருவாக்குவது.",
    "பைதான்": "பைதான் ஒரு நிரலாக்க மொழி."
}

# 📜 Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input
prompt = st.chat_input("Ask your doubt (English / Tamil)...")

# 🚫 Limit
if prompt and len(prompt) > 200:
    st.warning("⚠️ Ask short questions (max 200 chars)")
    st.stop()

# ➕ Math solver
def solve_math(q):
    try:
        if re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q):
            return str(eval(q))
    except:
        return None

# 🤖 API
def get_ai_response(user_prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=SYSTEM_PROMPT + "\n\nQ: " + user_prompt
        )
        return response.text if response.text else "No response."
    except:
        return "⚠️ API_LIMIT"

# 🚀 MAIN
if prompt:

    user_q = prompt.lower().strip()

    # 👤 Show user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 💾 Cache
    if user_q in st.session_state.cache:
        reply = st.session_state.cache[user_q]

    # ➕ Math
    elif solve_math(user_q):
        reply = f"Answer: {solve_math(user_q)}"

    # 🌐 Tamil
    elif any(word in prompt for word in TAMIL_DB):
        for word in TAMIL_DB:
            if word in prompt:
                reply = TAMIL_DB[word]
                break

    # 📚 Offline
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # 🤖 API
    else:
        time.sleep(4)
        with st.spinner("Thinking..."):
            reply = get_ai_response(prompt)

    # 🔄 Fallback
    if "⚠️" in reply:
        reply = "⚡ நான் Free Mode-ல் இருக்கேன். Simple questions கேளுங்கள் 😊"

    # 💾 Save
    st.session_state.cache[user_q] = reply

    # 🤖 Show
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
