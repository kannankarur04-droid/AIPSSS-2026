import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import base64
import fitz # PyMuPDF

# --- 🔐 API ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("❌ Missing GROQ_API_KEY")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖")

# --- 🎨 CLEAN CSS (NO BREAK UI) ---
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

/* Header layout */
.header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

/* Logo fix */
.logo {
    width: 90px;
    height: auto;
}

/* Title fix */
.title {
    font-size: 32px;
    font-weight: bold;
    color: #FF4B4B;
}

/* Tagline */
.tagline {
    font-size: 14px;
    color: #aaa;
}

/* Mobile fix */
@media (max-width: 600px) {
    .header {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 🖼️ LOGO LOAD ---
def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo = get_base64("aipsss_robot_final.png")

# --- HEADER ---
if logo:
    st.markdown(f"""
    <div class="header">
        <img src="data:image/png;base64,{logo}" class="logo">
        <div>
            <div class="title">AIPSSS</div>
            <div class="tagline">AI Powered Student Support System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("AIPSSS")

# --- 🎤 VOICE ---
voice = speech_to_text(
    start_prompt="🎤 பேச",
    stop_prompt="🛑 நிறுத்த",
    language="ta-IN",
    key="mic"
)

# --- 📂 PDF ---
pdf_text = ""
file = st.file_uploader("📂 Upload PDF", type=["pdf"])

if file:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for p in doc:
        pdf_text += p.get_text()
    st.success("✅ PDF loaded")

# --- 🧠 AI FUNCTION ---
def get_ai(q):
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Educational assistant. Answer clearly."},
                {"role": "user", "content": q + pdf_text[:1000]}
            ]
        )
        return res.choices[0].message.content
    except Exception:
        return "⚠️ AI busy. Try again."

# --- INPUT ---
text = st.chat_input("Ask your question...")

query = voice if voice else text

# --- RESPONSE ---
if query:
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ans = get_ai(query)
            st.write(ans)

            # --- 🔊 VOICE OUTPUT ---
            try:
                lang = "ta" if re.search(r'[\u0B80-\u0BFF]', ans) else "en"
                tts = gTTS(ans[:300], lang=lang)
                tts.save("res.mp3")
                st.audio("res.mp3")
            except:
                pass
