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

# --- 🎨 2. Styling (CSS) - அலைன்மென்ட் திருத்தம் ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; }

    /* Header Container - முற்றிலும் சீரமைக்கப்பட்டது */
    .aipsss-header {
        display: flex;
        flex-direction: column; 
        align-items: flex-start; /* இடது பக்கமாக அலைன் செய்ய */
        justify-content: flex-start;
        padding-left: 50px;
        margin-bottom: -10px; /* கேள்வி பெட்டிக்கு மிக அருகில் கொண்டு வர */
    }

    /* லோகோ - பெரிய அளவில், கேள்வி பெட்டியை மிதிப்பது போன்ற தோற்றம் */
    .main-logo {
        width: 320px !important; 
        height: auto;
        margin-bottom: -20px; /* கால்கள் பெட்டியைத் தொட */
    }

    /* Content Box - மாணவனின் காலுக்கு நேராக அமைய */
    .content-box {
        padding-left: 20px; /* மாணவனின் காலுக்கு நேராக வர இந்த padding உதவும் */
    }

    /* AI STUDENT MENTOR - RED Color */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 55px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 1.0 !important;
        text-transform: uppercase;
    }

    /* Tagline - White */
    .subtitle {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; 
        margin: 5px 0 0 0 !important;
        font-style: italic;
    }

    /* Developer - Gold (மாணவனின் காலுக்கு நேராக அமைய) */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 16px !important;
        color: #FFD700 !important; 
        margin: 2px 0 0 0 !important;
        font-weight: 600;
    }

    /* Input Box Alignment */
    .stChatInputContainer { margin-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 4. Header Display Logic ---
base64_img = None 
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI STUDENT MENTOR</h1>
                <p class="subtitle">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. Chat History & Engine ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def ai_response(user_query):
    try:
        system_instruction = "You are AI Student Mentor. Be precise."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": user_query}]
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")

if text_input:
    st.session_state.messages.append({"role": "user", "content": text_input})
    with st.chat_message("user"): st.markdown(text_input)
    with st.chat_message("assistant"):
        reply = ai_response(text_input)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
