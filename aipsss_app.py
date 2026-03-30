import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import base64
import fitz # PyMuPDF

# ---------------- 🔐 SETUP ----------------
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🎓")

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("❌ Missing GROQ_API_KEY!")
    st.stop()

# ---------------- 🎨 CSS FIX ----------------
st.markdown("""
<style>

/* FULL WIDTH FIX */
.block-container {
    padding-top: 1rem;
    max-width: 100% !important;
}

/* Header */
.header-wrapper {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 25px;
    width: 100%;
    overflow: visible !important;
}

/* Logo */
.logo-img {
    width: 120px;
    height: auto;
    object-fit: contain;
}

/* Title */
.main-title {
    font-size: 34px !important;
    font-weight: 900;
    color: #FF4B4B;
    margin: 0;
    line-height: 1.2;
    white-space: nowrap;
}

/* Tagline */
.main-tagline {
    font-size: 15px;
    color: #555;
    font-weight: bold;
}

/* Caption */
.logo-caption {
    font-size: 11px;
    color: #888;
}

/* Prevent cut */
div {
    overflow: visible !important;
}

/* Mobile fix */
@media (max-width: 768px) {
    .header-wrapper {
        flex-direction: column;
        text-align: center;
    }

    .main-title {
        font-size: 26px !important;
        white-space: normal;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- 🖼️ LOGO ----------------
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

encoded_img = get_base64_image("aipsss_robot_final.png")

if encoded_img:
    st.markdown(f"""
    <div class="header-wrapper">
        <div>
            <img src="data:image/png;base64,{encoded_img}" class="logo-img">
            <div class="logo-caption">Developed by Kannan</div>
        </div>

        <div style="flex:1;">
            <div class="main-title">AIPSSS</div>
            <div class="main-tagline">AI Powered Student Support System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("AIPSSS")

# ---------------- 🎤 VOICE ----------------
voice_input = speech_to_text(
    start_prompt="🎤 பேச",
    stop_prompt="🛑 நிறுத்த",
    language='ta-IN',
    use_container_width=True,
    key='mic'
)

# ---------------- 🧠 AI ----------------
def ai_response(q, pdf_text=""):
    try:
        context = f"Context: {pdf_text[:1500]}" if pdf_text else ""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an educational assistant. Answer clearly in Tamil or English."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.2
        )

        return completion.choices[0].message.content

    except Exception:
        return "⚠️ Server busy. Please try again."

# ---------------- 📂 PDF ----------------
uploaded_pdf = st.file_uploader("📂 PDF upload", type=["pdf"])
pdf_context = ""

if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF Loaded")

# ---------------- 💬 INPUT ----------------
text_input = st.chat_input("Ask your question...")

prompt = voice_input if voice_input else text_input

# ---------------- 🚀 RESPONSE ----------------
if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ai_response(prompt, pdf_context)
            st.write(reply)

            # 🔊 Voice output
            try:
                lang = 'ta' if re.search(r'[\u0b80-\u0bff]', reply) else 'en'
                tts = gTTS(text=reply[:300], lang=lang)
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
