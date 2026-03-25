import streamlit as st
from google import genai
import time
import re

# 🔑 API (replace with your key)
client = genai.Client(api_key="YOUR_API_KEY")

# 🎨 UI
st.set_page_config(page_title="AIPSSS Stable", layout="wide")
st.title("🎓 AI Student Support System")

# 💾 Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📚 Offline DB
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data and performs tasks.",
    "what is commerce": "Commerce is the activity of buying and selling goods and services.",
    "what is ai": "Artificial Intelligence is intelligence shown by machines.",
}

# 📜 Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input
prompt = st.chat_input("Ask your question...")

# ➕ Math detect
def extract_math(q):
    match = re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q)
    return match.group() if match else None

# 🧠 Expert logic
def expert_answer(q):
    q = q.lower()

    # Explain mode FIRST
    if "explain" in q:

        if "commerce" in q:
            return """Commerce is the activity of buying and selling goods and services.

• Connects producers and consumers  
• Includes trade and business  
• Helps economic growth  
• Involves transport and communication  
• Important for markets  
"""

        if "ai" in q:
            return """AI uses:
• Healthcare – Disease detection  
• Education – Smart learning  
• Business – Chatbots  
• Automation – Robots  
• Security – Fraud detection  
"""

    # Short definitions
    if "computer" in q:
        return "A computer is an electronic device that processes data."

    if "commerce" in q:
        return "Commerce is buying and selling of goods and services."

    return None

# 🤖 API (UPDATED MODEL ✅)
def get_ai_response(q):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",   # ✅ WORKING MODEL
            contents="Explain simply:\n\n" + q
        )
        return response.text
    except Exception as e:
        return None

# 🚀 MAIN
if prompt:

    user_q = prompt.lower().strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None

    # 1️⃣ Math
    math_expr = extract_math(user_q)
    if math_expr:
        reply = f"Calculation Result: {math_expr} = {eval(math_expr)}"

    # 2️⃣ Expert logic
    elif expert_answer(user_q):
        reply = expert_answer(user_q)

    # 3️⃣ Offline DB
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # 4️⃣ API (only if needed)
    else:
        with st.spinner("Thinking..."):
            time.sleep(2)
            reply = get_ai_response(prompt)

    # 5️⃣ FINAL fallback (no error shown ❌)
    if not reply:
        reply = "⚠️ AI temporarily unavailable. Showing basic knowledge only."

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
