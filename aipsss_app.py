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

# 📚 Basic Offline DB
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

# 🧠 Expert logic
def expert_answer(q):
    q = q.lower()

    # Subjects
    if any(w in q for w in ["physics", "force", "energy"]):
        return "Physics is the study of matter and energy."

    if any(w in q for w in ["commerce", "business", "economics"]):
        return "Commerce deals with buying and selling goods."

    if any(w in q for w in ["biology", "plants", "animals"]):
        return "Biology is the study of living organisms."

    if any(w in q for w in ["computer", "software", "hardware"]):
        return "Computers process data using hardware and software."

    # Explain AI
    if "explain" in q and "ai" in q:
        return """AI uses:
• Healthcare – Disease detection  
• Education – Smart learning  
• Business – Chatbots  
• Automation – Robots  
• Security – Fraud detection  
"""

    # Tamil
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
