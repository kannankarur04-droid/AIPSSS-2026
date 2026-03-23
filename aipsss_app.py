import streamlit as st
from google import genai
import time
import re

# 🔑 API
client = genai.Client(api_key="YOUR_API_KEY")

# 🎨 UI
st.set_page_config(page_title="AIPSSS Expert", layout="wide")
st.title("🎓 AI Student Support System (Expert Mode)")

# 💾 Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📚 Offline DB
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data.",
    "what is ai": "Artificial Intelligence is intelligence shown by machines.",
    "what is commerce": "Commerce is buying and selling of goods and services.",
    "what is electronics": "Electronics deals with circuits and electronic devices.",
}

# 📜 Show chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input
prompt = st.chat_input("Ask your question...")

# ➕ Math detect
def extract_math(q):
    match = re.search(r'[0-9]+\s*[\+\-\*/]\s*[0-9]+', q)
    return match.group() if match else None

# 🧠 Expert logic (FIXED 🔥)
def expert_answer(q):
    q = q.lower()

    # 📘 Basic subjects
    if "physics" in q:
        return "Physics is the study of matter, energy, and forces."

    if "commerce" in q:
        return "Commerce is buying and selling of goods and services."

    if "biology" in q:
        return "Biology is the study of living organisms."

    if "electronics" in q:
        return "Electronics deals with circuits and electronic devices."

    # 🧠 Explain mode (topic-based)
    if "explain" in q:

        if "ai" in q:
            return """AI uses:
• Healthcare – Disease detection  
• Education – Smart learning  
• Business – Chatbots  
• Automation – Robots  
• Security – Fraud detection  
"""

        if "radiation" in q:
            return """Radiation is the emission of energy as waves or particles.

• Travels through space  
• Can be natural or man-made  
• Used in medical treatment  
• Harmful at high levels  
• Includes X-rays and gamma rays  
"""

        if "computer" in q:
            return """Computer is an electronic device.

• Takes input  
• Processes data  
• Produces output  
• Stores information  
• Used everywhere  
"""

    # 🌐 Tamil support
    if "கணினி" in q:
        return "கணினி என்பது தகவலை செயலாக்கும் மின்னணு சாதனம்."

    return None

# 🤖 API
def get_ai_response(q):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Explain simply:\n\n" + q
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

    # 1️⃣ Math
    math_expr = extract_math(user_q)
    if math_expr:
        try:
            reply = f"Answer: {eval(math_expr)}"
        except:
            reply = None

    # 2️⃣ Expert logic
    elif expert_answer(user_q):
        reply = expert_answer(user_q)

    # 3️⃣ Offline DB
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # 4️⃣ API
    else:
        with st.spinner("Thinking..."):
            time.sleep(2)
            reply = get_ai_response(prompt)

    # 5️⃣ Fallback
    if not reply:
        reply = "⚠️ AI busy. Try simple or subject-based questions."

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
