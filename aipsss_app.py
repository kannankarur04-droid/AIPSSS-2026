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
    st.error("Missing GROQ_API_KEY! Please check your Streamlit secrets.")
    st.stop()

# --- 🎨 2. Styling (The "Perfect Alignment" Design) ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1000px; }

    /* Custom Header Container */
    .mentor-header {
        display: flex;
        align-items: flex-end; /* பெட்டியின் மேல் கால் வைக்கும் தோற்றம் */
        gap: 25px;
        margin-bottom: -18px; /* கேள்வி பெட்டியுடன் இணைக்க */
        padding-left: 20px;
    }

    /* Logo - Big & Stepping on Input Box */
    .header-logo {
        width: 280px !important; 
        height: auto;
        margin-bottom: -12px; /* காலுக்கும் பெட்டிக்கும் இடைவெளி குறைக்க */
        z-index: 10;
    }

    /* Header Text Box - Tight Line Spacing */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding-bottom: 25px; /* வரிகளை சற்று உயர்த்த */
    }

    /* AI STUDENT MENTOR - RED */
    .header-text h1 {
        font-family: 'Lexend', sans-serif;
        font-size: 55px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; /* மிக நெருக்கமான வரி */
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
