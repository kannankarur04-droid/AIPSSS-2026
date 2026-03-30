import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image # லோகோவைக் கையாள
import fitz  # PyMuPDF

# --- 🔐 1. API Key Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. UI Styling ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🎓")

st.markdown("""
    <style>
    /* தலைப்பைச் சுருக்க */
    .block-container { padding-top: 1rem; }
    
    /* மைக் பட்டன் - பெரியதாகவும் சிவப்பு நிறத்திலும் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Placement (தலைப்புக்கு பதிலாக) ---
try:
    # GitHub-ல் லோகோ படம் இருந்தால் அதைப் பதிவேற்றும்
    logo_path = os.path.join(os.path.dirname(__file__), 'aipsss_logo.png')
    logo_image = Image.open(logo_path)
    
    col1, col2, col3 = st.columns([1, 2, 1]) # நடுவில் லோகோ வைக்க
    with col2:
        st.image(logo_image, use_container_width=True)
        
except FileNotFoundError:
    # லோகோ படம் இல்லையென்றால், பழையபடி 'AIPSSS' என்று மட்டும் காட்டும்
    st.markdown('<p style="font-size: 40px !important; font-weight: 900; text-align: center; margin-top: -60px; color: #FF4B4B; letter-spacing: 2px;">AIPSSS</p>', unsafe_allow_html=True)

# --- 🧠 4. AI Logic (தொடரும்...) ---
# PDF, Voice மற்றும் Output பகுதிகள் முந்தைய கோடில் அதேபோல் தொடரும்
