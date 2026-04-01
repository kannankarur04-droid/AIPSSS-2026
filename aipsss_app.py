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

# --- 🎨 2. Styling (CSS) ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1200px; }

    /* லோகோ மற்றும் எழுத்துக்களை இணைக்கும் மெயின் கண்டெய்னர் */
    .mentor-header {
        display: flex;
        align-items: center; /* செங்குத்தாக நடுவில் வைக்க */
        gap: 20px;
        padding: 10px 0;
        margin-bottom: 10px;
    }

    /* லோகோ அளவு */
    .header-logo {
        width: 120px !important; 
        height: auto;
    }

    /* எழுத்துக்களின் பெட்டி */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* AI STUDENT MENTOR - சிகப்பு நிறம் */
    .header-text h1 {
        font-family: 'Lexend', sans-serif;
        font-size: 45px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 1.0 !important; 
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    /* Tagline - வெள்ளை நிறம் */
    .tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 18px !important;
        color: #FFFFFF !important; 
        margin: 5px 0 2px 0 !important;
        font-style: italic;
        line-height: 1.2 !important;
    }

    /* Developer - தங்க நிறம் */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 14px !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* Chat Input Styling */
    .stChatInputContainer { border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Display Logic ---
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')
base64_img = get_base64_image(img_path)

if base64_img:
    st.markdown(f'''
        <div class="mentor-header">
            <img src="data:image/png;base64,{base64_img}" class="header-logo">
            <div class="header-text">
                <h1>AI STUDENT MENTOR</h1>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    # லோகோ படம் இல்லை என்றால் மட்டும் இது தெரியும்
    st.markdown('''
        <div style="padding-left:20px;">
            <h1 style="color:#FF4B4B; margin:0;">AI STUDENT MENTOR</h1>
            <p style="color:white; font-style:italic; margin:0;">"Everyone has the right to education"</p>
            <p style="color:#FFD700; font-weight:bold; margin:0;">Developed by Brammadevan</p>
        </div>
    ''', unsafe_allow_html=True)

# --- 🤖 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        system_instruction = "You are AI Student Mentor. Answer precisely."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

uploaded_pdf = st.file_uploader("📂 PDF கோப்புகள்", type=["pdf"])
pdf_extracted_text = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])

voice_input = speech_to_text(start_prompt="🎤 பேச", language='ta-IN', use_container_width=True, key='mic_v1')
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")
prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except: pass
    st.session_state.messages.append({"role": "assistant", "content": reply})
