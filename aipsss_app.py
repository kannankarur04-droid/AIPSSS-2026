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

# --- 🎨 2. Styling (CSS) - Sidebar Logo Style ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓") # Wide layout for better side alignment

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 1200px; }
    
    /* Header Container - லோகோ ஓரத்தில் வர */
    .aipsss-header {
        display: flex;
        align-items: center; /* லோகோ மற்றும் டெக்ஸ்ட் மையமாக அலைன் ஆக */
        justify-content: flex-start;
        gap: 30px; 
        margin-bottom: 40px;
        background: rgba(255, 255, 255, 0.05); /* ஒரு மெல்லிய பின்னணி */
        padding: 20px;
        border-radius: 20px;
    }

    /* லோகோவை ஓரத்தில் பெரிதாக்க (300px) */
    .main-logo {
        width: 300px; 
        height: auto;
        object-fit: contain;
        filter: drop-shadow(0px 0px 10px rgba(255, 75, 75, 0.3));
    }

    /* டெக்ஸ்ட் பாக்ஸ் */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    .main-title {
        font-size: 5.5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 1 !important;
    }

    .subtitle {
        font-size: 1.8rem !important;
        color: #FFD700 !important; /* Gold */
        margin: 0 !important;
        font-weight: bold !important;
        padding-top: 10px;
    }

    .quote-text {
        font-size: 1.3rem !important;
        font-style: italic !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 5px;
    }

    .developer {
        font-size: 1.2rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        padding-top: 5px;
        font-weight: 500;
    }

    /* Mobile View Fix */
    @media (max-width: 768px) {
        .aipsss-header { flex-direction: column; text-align: center; gap: 15px; padding: 15px; }
        .main-logo { width: 150px !important; }
        .main-title { font-size: 3rem !important; }
        .subtitle { font-size: 1.1rem !important; }
    }

    .stButton > button { height: 75px !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
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
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "gaming", "cheat", "hack", "illegal", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான வழிகாட்டி மட்டுமே."

        system_instruction = "You are AIPSSS, a professional Education Mentor. Answer based on provided PDF or general knowledge. Strictly no gaming/entertainment."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])

pdf_extracted_text = ""
if uploaded_pdf:
    with st.spinner("PDF Reading..."):
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ '{uploaded_pdf.name}' Loaded!")

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_sidebar_style')
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            try:
