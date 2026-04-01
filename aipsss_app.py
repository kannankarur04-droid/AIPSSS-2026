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

# --- 🎨 2. UI/UX Design (Kannan's Gentle View Layout) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Box - Reverse Row for Logo on Right */
    .aipsss-header {
        display: flex;
        flex-direction: row-reverse; /* லோகோவை வலது பக்கம் நகர்த்த */
        align-items: center; 
        justify-content: space-between; /* எழுத்துக்களுக்கும் லோகோவுக்கும் இடையே இடைவெளி */
        gap: 40px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.07); 
        padding: 35px 50px;
        border-radius: 20px;
        flex-wrap: nowrap;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo - Right Side */
    .main-logo {
        height: auto;
        width: 320px !important; 
        max-height: 280px;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* Content Box - Left side but moved slightly right */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
        padding-left: 20px; /* எழுத்துக்களைச் சிறிது வலதுபுறம் நகர்த்த */
    }

    .main-title {
        font-size: 5.5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 0.75 !important; /* லைன் ஸ்பேஸ் குறைக்கப்பட்டுள்ளது */
        letter-spacing: -3px;
    }

    .subtitle {
        font-size: 1.8rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: 700 !important;
        line-height: 1.0 !important; /* லைன் ஸ்பேஸ் குறைக்கப்பட்டுள்ளது */
        padding-top: 12px;
    }

    .quote-text {
        font-size: 1.2rem !important;
        font-style: italic !important;
        color: #ffffff !important; 
        margin: 0 !important;
        padding-top: 5px; /* இடைவெளி குறைப்பு */
        opacity: 0.8;
    }

    .developer {
        font-size: 1.1rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 3px;
        font-weight: 600;
    }

    /* Mobile Responsive - Strict Design */
    @media (max-width: 768px) {
        .aipsss-header { 
            flex-direction: row-reverse; /* மொபைலிலும் லோகோ வலதுபுறம் */
            gap: 15px; 
            padding: 15px; 
        }
        .main-logo { width: 110px !important; }
        .content-box { padding-left: 5px; }
        .main-title { font-size: 2.2rem !important; line-height: 0.8 !important; }
        .subtitle { font-size: 0.8rem !important; line-height: 1.0 !important; }
        .quote-text, .developer { font-size: 0.65rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Display Logic ---
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
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by KANNAN (Brammadevan)</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
