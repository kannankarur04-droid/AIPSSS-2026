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

# --- 🎨 2. Styling (Logo Enlarged & Side-by-Side Fix) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Container - Strict Side-by-Side */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 20px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px;
        border-radius: 25px;
        flex-wrap: nowrap; /* அடுத்த வரிக்குச் செல்லாமல் தடுக்க */
    }

    /* Logo Styling - கம்ப்யூட்டரில் பெரிதாக்கப்பட்டுள்ளது (380px) */
    .main-logo {
        height: auto;
        width: 380px !important; 
        max-height: 280px;
        object-fit: contain;
        flex-shrink: 0; /* லோகோ சுருங்காமல் இருக்க */
    }

    /* Content Box - Spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
        overflow: hidden;
    }

    .main-title {
        font-size: 5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 0.8 !important;
        letter-spacing: -2px;
    }

    .subtitle {
        font-size: 1.6rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        padding-top: 10px;
        white-space: nowrap; 
    }

    .quote-text {
        font-size: 1.2rem !important;
        font-style: italic !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 5px;
        white-space: nowrap;
    }

    .developer {
        font-size: 1.1rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        padding-top: 5px;
        opacity: 0.9;
    }

    /* Mobile Responsive - Strict Side-by-Side */
    @media (max-width: 768px) {
        .aipsss-header { 
            gap: 12px; 
            padding: 12px;
            margin-top: 15px;
        }
        .main-logo { 
            width: 150px !important; /* மொபைலில் லோகோவின் அகலம் உயர்த்தப்பட்டுள்ளது */
            height: auto !important;
        }
        .main-title { font-size: 2.5rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.85rem !important; padding-top: 5px; white-space: normal; }
        .quote-text, .developer { font-size: 0.75rem !important; white-space: normal; }
        .content-box { gap: 3px; }
    }

    .stButton > button { height: 65px !important; border-radius: 12px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(path):
    if os.
