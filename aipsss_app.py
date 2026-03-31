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

# --- 🎨 2. Styling (CSS) - Ultra Precise Responsive ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    
    /* Header Container - Flexible for Mobile */
    .aipsss-header {
        display: flex;
        align-items: flex-end; /* Text sits at the bottom of the logo */
        justify-content: flex-start;
        gap: 15px; /* Spacing between logo and text */
        margin-bottom: 35px;
        margin-top: 20px;
        width: 100%;
    }

    /* Logo Size - Enlarged as requested */
    .main-logo {
        width: 220px; /* லோகோவை பெரிதாக்கியுள்ளேன் */
        height: auto;
        object-fit: contain;
    }

    /* Content Box - Stacked lines on the left */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        text-align: left;
    }

    /* Desktop Sizes */
    @media (min-width: 769px) {
        .main-logo { width: 220px; height: auto; }
        .main-title { font-size: 4.8rem !important; color: #ff4d4d !important; margin: 0 !important; font-weight: 900 !important; line-height: 0.8 !important; }
        .subtitle { font-size: 1.6rem !important; }
        .quote-text { font-size: 1.15rem !important; }
        .developer { font-size: 1rem !important; }
    }

    /* Mobile View - Center everything */
    @media (max-width: 768px) {
        .aipsss-header { flex-direction: column; align-items: center; text-align: center; gap: 15px; }
        .content-box { text-align: center; }
        .main-logo { width: 180px; }
        .main-title { font-size: 3.2rem !important; }
        .subtitle { font-size: 1.2rem !important; }
        .developer { font-size: 0.9rem !important; }
    }

    .main-title { font-weight: 900 !important; color: #ff4d4d !important; margin: 0 !important; }
    .subtitle { color: #FFD700 !important; margin: 0 !important; font-weight: bold !important; line-height: 1.0 !important; padding-top: 8px; }
    .quote-text { font-style: italic !important; color: #FFD700 !important; margin: 0 !important; line-height: 1.0 !important; padding-top: 4px; }
    .developer { color: #FFFFFF !important; opacity: 0.8 !important; margin: 0 !important; line-height: 1.0 !important; padding-top: 5px; }

    /* UI Styles */
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20
