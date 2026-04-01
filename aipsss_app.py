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

# --- 🎨 2. Styling (CSS) - Optimized for Slim Look ---
st.set_page_config(page_title="AI STUDENTS MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* Background Color */
    .stApp { background-color: #0E1117; }
    block-container { 
        padding-top: 5rem !important; /* 1rem லிருந்து 5rem ஆக உயர்த்தப்பட்டுள்ளது */
        max-width: 1200px; 
    }
    
    /* Slim Header Container */
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 30px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px 30px; /* Padding சற்று கூட்டப்பட்டுள்ளது */
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Smaller Logo */
    main-logo {
        width: 50px !important; /* 100px லிருந்து 160px ஆக உயர்த்தப்பட்டுள்ளது */
        height: auto;
        object-fit: contain;
    }

    /* Content Box with minimal line spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* Title in one line and Red color */
    .main-title { 
        font-size: 2.2rem !important;
        font-weight: 800; 
        color: #FF4B4B !important;
        text-transform: uppercase;
        margin: 0 !important; 
        padding: 0 !important;
        line-height: 1.0 !important;
        white-space: nowrap;
    }

    /* Subtitle and Developer with very low spacing */
    .subtitle {
        font-size: 1.0rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 2px !important;
        font-weight: bold !important;
    }

    .developer {
        font-size: 0.9rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        padding-top: 0px !important;
        opacity: 0.8;
    }

    /* Button and Input Styling */
    .stButton > button { height: 50px !important; border-radius: 10px !important; background-color: #1E1E1E !important; color: white !important; border: 1px solid #333 !important; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header ---
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
                <h1 class="main-title">AI STUDENTS MENTOR</h1>
                <p class="subtitle">Everyone has the right to education</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "gaming", "play", "pubg", "cheat", "hack", "illegal", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி தொடர்பான வழிகாட்டி மட்டுமே."

        system_instruction = "You are AIPSSS, a professional Education Mentor for students. Answer clearly."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Implementation ---

# PDF Section
st.markdown("📂 **PDF மூலம் தேடுவதற்கு**")
uploaded_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
pdf_extracted_text = ""

if uploaded_pdf:
    with st.spinner("PDF Reading..."):
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ {uploaded_pdf.name} Loaded!")

# Voice Input Button
voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_vfinal')

# Chat messages display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Logic
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
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
