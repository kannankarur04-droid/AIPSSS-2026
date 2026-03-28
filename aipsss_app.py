import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
from langdetect import detect
import os

# --- 🔐 API Key Setup ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

# --- 🎨 UI Setup ---
st.set_page_config(page_title="AIPSSS Expert Voice", layout="wide", page_icon="🎓")

# --- 💅 CSS Styling (வண்ணங்கள் மற்றும் லோகோ வடிவமைப்பு) ---
st.markdown("""
<style>
    .stApp { background-color: #f0faff; }
    .main-title {
        color: #1a5276;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .logo-container { text-align: center; margin-bottom: 20px; }
    .assistant-box {
        background-color: #ffffff;
        border-left: 6px solid #2980b9;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
