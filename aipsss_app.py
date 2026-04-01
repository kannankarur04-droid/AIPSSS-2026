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

# --- 🎨 2. Styling (CSS) - 'Final Logo' Design ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

# CSS - இங்கேதான் வரிசை 20 தொடங்குகிறது
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1000px; }

    /* Custom Header Container */
    .mentor-header {
        display: flex;
        align-items: flex-end; 
        gap: 25px;
        margin-bottom: -18px; 
        padding-left: 20px;
    }

    /* Logo - Big & Stepping on Input Box */
    .header-logo {
        width: 280px !important; 
        height: auto;
        margin-bottom: -12px; 
        z-index: 10;
    }

    /* Header Text Box - Tight Line Spacing */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding-bottom: 25px; 
    }

    /* AI STUDENT MENTOR - RED */
    .header-text h1 {
        font-family: 'Lexend', sans-serif;
        font-size: 55px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; 
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* Tagline - White */
    .tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; 
        margin: 6px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* Developer - Gold */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 16px !important;
        color: #FFD700 !important; 
        margin: 4px 0 0 0 !important;
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Buttons */
    .stButton > button { height: 60px !important; border-radius: 12px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True) # <--- இங்கே வரிசை 61-ல் சரியாக மூடப்பட்டுள்ளது

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Display Logic ---
base64_img = None 
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    st.markdown(f'''
        <header class="mentor-header">
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="header-logo">
            <div class="header-text">
                <h1>AI STUDENT MENTOR</h1>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </header>
    ''', unsafe_allow_html=True)

# --- 🤖 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        system_instruction = "You are AI Student Mentor. Be precise."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf_extracted_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

uploaded_pdf = st.file_uploader("📂 PDF", type=["pdf"])
pdf_extracted_text = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])

prompt = st.chat_input("கேள்வியைக் கேட்கவும்...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = ai_response(prompt, pdf_extracted_text)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
