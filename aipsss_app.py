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

# --- 🎨 2. UI/UX Design (Kannan's 100% Satisfied Layout) ---
st.set_page_config(page_title="AI Smart Mentor", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 1300px; }
    
    /* Header Box - Designed for "Gentle View" */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 40px; 
        margin-bottom: 35px;
        background: rgba(255, 255, 255, 0.06); 
        padding: 40px 50px;
        border-radius: 25px;
        flex-wrap: nowrap;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo - Enlarged as requested */
    .main-logo {
        height: auto;
        width: 400px !important; /* லோகோ இன்னும் பெரிதாக்கப்பட்டுள்ளது */
        max-height: 320px;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* Content Box - Right Side Typography with reduced line spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    .main-title {
        font-size: 5.8rem !important; /* AI Smart Mentor Title */
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 0.85 !important; /* கச்சிதமான லைன் ஸ்பேஸ் */
        letter-spacing: -3px;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.2);
    }

    .quote-text {
        font-size: 1.6rem !important; /* "Everyone has the right to education" */
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: 600 !important;
        line-height: 1.1 !important;
        padding-top: 15px;
        font-style: italic;
    }

    .developer {
        font-size: 1.2rem !important; /* Developed by Brammadevan */
        color: #ffffff !important; 
        margin: 0 !important;
        padding-top: 8px;
        font-weight: 500;
        opacity: 0.9;
    }

    /* Mobile Responsive Logic */
    @media (max-width: 768px) {
        .aipsss-header { gap: 20px; padding: 20px; }
        .main-logo { width: 140px !important; }
        .main-title { font-size: 2.6rem !important; line-height: 0.9 !important; }
        .quote-text { font-size: 0.9rem !important; padding-top: 8px; }
        .developer { font-size: 0.8rem !important; padding-top: 4px; }
    }

    /* Professional Button */
    .stButton > button { 
        height: 65px !important; 
        border-radius: 15px !important; 
        background-color: #FF4B4B !important; 
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

if b64_img:
    st.markdown(f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{b64_img}" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI Smart Mentor</h1>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🧠 4. AI Engine (The Knowledge Hub) ---
def ai_response(q, pdf=""):
    try:
        sys_msg = "You are AI Smart Mentor, an Education Expert. Answer all subjects precisely. Temperature: 0.0."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Rest of the Speech-to-Text and UI code follows same logic as before...
