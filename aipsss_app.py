import streamlit as st
from google import genai
import time

# 🔑 API setup
client = genai.Client(api_key="AIzaSyD5U5-VOb6YchdkSDC6Xi4qRGnc-zablYg")

# 🎨 Page config
st.set_page_config(page_title="AIPSSS", layout="wide")
st.title("🎓 AI Powered Student Support System")

# 🧠 Short prompt (token save)
SYSTEM_PROMPT = "Explain simply with example. Use formulas if needed. Add 2 MCQs."

# 💾 Session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 💾 Cache (save API usage)
if "cache" not in st.session_state:
    st.session_state.cache = {}

# 📜 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ User input
prompt = st.chat_input("Ask your educational doubt...")

# 🔁 Function with retry
def get_ai_response(user_prompt):
    for i in range(3):  # retry 3 times
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=SYSTEM_PROMPT + "\n\nQ: " + user_prompt
            )
            return response.text if response.text else "No response."
        except Exception:
            time.sleep(5)
    return "⚠️ Server busy. Please try again later."

# 🚀 Main logic
if prompt:

    # 👤 Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 💾 Check cache
    if prompt in st.session_state.cache:
        reply = st.session_state.cache[prompt]
    else:
        time.sleep(2)  # ⏱ delay to avoid rate limit
        reply = get_ai_response(prompt)
        st.session_state.cache[prompt] = reply  # save cache

    # 🤖 Show AI response
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
