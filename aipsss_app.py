import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF
import base64

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (Perfect Alignment) ---
st.set_page_config(page_title="AI Smart Mentor", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 2rem !important; }

    /* Header Container - முற்றிலும் சீரமைக்கப்பட்டது */
    .header-container {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 45px; 
        margin-bottom: 40px;
        background: rgba(255, 255, 255, 0.03); 
        padding: 45px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* லோகோ - பெரிய அளவில் கம்பீரமாக */
    .logo-img {
        width: 160px !important; 
        height: auto;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* எழுத்துக்கள் பெட்டி - கச்சிதமான அலைன்மென்ட் */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* AI SMART MENTOR - Capitalized & Tight Line Space */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 52px !important; 
        color: #FF4B4B !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.85 !important;
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* பொன்மொழி - தூய வெள்ளை (White) */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; 
        margin: 10px 0 0 0 !important;
        font-weight: 500;
        font-style: italic;
    }

    /* டெவலப்பர் - தங்க நிறம் (Gold) */
    .dev-text {
        font-family: 'Lexend', sans-serif;
        font-size: 17px !important;
        color: #FFD700 !important; 
        margin: 8px 0 0 0 !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Mobile Responsive Logic */
    @media (max-width: 768px) {
        .header-container { gap: 20px; padding: 20px; flex-direction: row; }
        .logo-img { width: 90px !important; }
        .main-title { font-size: 24px !important; line-height: 0.9 !important; }
        .main-tagline { font-size: 12px !important; }
        .dev-text { font-size: 11px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Assets & Display ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

if b64_img:
    st.markdown(f'''
        <div class="header-container">
            <img src="data:image/png;base64,{b64_img}" class="logo-img">
            <div class="content-box">
                <h1 class="main-title">AI SMART MENTOR</h1>
                <p class="main-tagline">"Everyone has the right to education"</p>
                <p class="dev-text">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🤖 4. AI Engine & Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def ai_response(q, pdf=""):
    try:
        sys_msg = "You are AI Smart Mentor, an Education Expert. Be factual. Temp: 0.0."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF", type=["pdf"])
v_in = speech_to_text(start_prompt="🎤 பேச", language='ta-IN', use_container_width=True, key='mic_v_final')
t_in = st.chat_input("கேள்வியைக் கேட்கவும்...")
prompt = v_in if v_in else t_in

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        rep = ai_response(prompt)
        st.markdown(rep)
        try:
            tts = gTTS(text=rep[:300], lang='ta')
            tts.save("res.mp3")
            st.audio("res.mp3", autoplay=True)
        except: pass
    st.session_state.messages.append({"role": "assistant", "content": rep})
