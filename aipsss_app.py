import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import base64
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Logo Left, Text Right ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    
    /* லோகோ மற்றும் பெயரை ஒரே வரிசையில் வைக்க */
    .header-wrapper {
        display: flex;
        flex-direction: row; /* கிடைமட்டமாக (Horizontally) அடுக்க */
        align-items: center; /* செங்குத்தாக மையப்படுத்த */
        justify-content: flex-start; /* இடது பக்கம் ஒட்டியிருக்க */
        margin-top: -30px;
        margin-bottom: 20px;
        gap: 20px; /* லோகோவுக்கும் பெயருக்கும் இடையே இடைவெளி */
    }

    /* லோகோ அளவு */
    .logo-img {
        width: 130px; /* படத்திற்கு ஏற்றவாறு அகலம் */
        height: auto;
        display: block;
    }

    /* பெயருக்கான கண்டெய்னர் */
    .text-container {
        display: flex;
        flex-direction: column; /* தலைப்பையும் கேப்ஷனையும் செங்குத்தாக அடுக்க */
        align-items: flex-start; /* இடது பக்கம் ஒட்டியிருக்க */
    }

    /* AIPSSS தலைப்பு */
    .main-title { 
        font-size: 50px !important; 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B;
        margin: 0;
        line-height: 1;
    }
    
    /* கேப்ஷன் */
    .main-tagline {
        font-size: 16px !important; 
        text-align: left; 
        color: #555;
        margin-top: 5px;
        font-weight: bold;
    }
    
    /* மைக் பட்டன் ஸ்டைல் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }

    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Logic (Base64) ---
img_name = 'aipsss_robot_final.png' 

def get_base64_image(path):
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

encoded_img = get_base64_image(img_name)

if encoded_img:
    # HTML & CSS பயன்படுத்தி லோகோவை இடதுபுறமும், பெயரை வலதுபுறமும் காட்ட
    st.markdown(f'''
        <div class="header-wrapper">
            <img src="data:image/png;base64,{encoded_img}" class="logo-img">
            <div
