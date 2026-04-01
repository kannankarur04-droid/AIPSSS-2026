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

# --- 🎨 2. UI/UX Design (Modern Typography & Kannan's Gentle View) ---
st.set_page_config(page_title="AI Smart Mentor", layout="wide", page_icon="🤖🎓")

# கூகுள் ஃபான்ட் 'Lexend' இணைக்கப்பட்டுள்ளது (Clean & Modern)
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 1300px; }
    
    /* Header Box */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 35px; 
        margin-bottom: 35px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 30px 45px;
        border-radius: 20px;
        flex-wrap: nowrap;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Lexend', sans-serif; /* நவீன ஃபான்ட் */
    }

    /* Logo - Scaled to fit single line text */
    .main-logo {
        height: auto;
        width: 250px !important; 
        max-height: 200px;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* Content Box */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* AI Smart Mentor - ஒரே வரியில் வர அளவு குறைக்கப்பட்டுள்ளது */
    .main-title {
        font-size: 3.8rem !important; 
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 1.0 !important;
        letter-spacing: -1.5px;
        white-space: nowrap; /* இதுதான் ஒரே வரியில் வைக்கும் */
    }

    .quote-text {
        font-size: 1.3rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: 400 !important;
        line-height: 1.2 !important;
        padding-top: 8px;
    }

    .developer {
        font-size: 1rem !important;
        color: #ffffff !important; 
        margin: 0 !important;
        padding-top: 4px;
        opacity: 0.8;
    }

    /* Mobile View - Responsive */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 15px; }
        .main-logo { width: 90px !important; }
        .main-title { font-size: 1.8rem !important; letter-spacing: -0.5px; }
        .quote-text { font-size: 0.75rem !important; padding-top: 5px; }
        .developer { font-size: 0.7rem !important; }
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
                <h1 class="main-title">AI Smart Mentor</h1>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
