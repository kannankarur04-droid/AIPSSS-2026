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

# --- 🎨 2. Styling (CSS) - Designer's Perfect Layout ---
st.set_page_config(page_title="AI Smart Mentor", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    /* Background & Container */
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 2rem !important; }

    /* Header Container - Flexible & Centered */
    .header-container {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 45px; 
        margin-bottom: 40px;
        background: rgba(255, 255, 255, 0.03); 
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo - BIGGER & Lowered */
    .logo-img {
        width: 190px !important; /* லோகோ மீண்டும் பெரிதாக்கப்பட்டுள்ளது */
        height: auto;
        object-fit: contain;
        flex-shrink: 0;
        margin-top: 15px; /* லோகோவைச் சற்று கீழே இறக்க */
    }

    /* Text Content Box - Lowered for perfect vertical alignment */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-top: 20px; /* தலைப்பைச் சற்று கீழே இறக்க */
    }

    /* AI SMART MENTOR - RED Color & Tight Line Space */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 52px !important; 
        color: #FF4B4B !important; /* நீங்கள் கேட்ட சிகப்பு நிறம் (Red) */
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.85 !important; /* மிகக் குறைவான வரி இடைவெளி */
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* Tagline - Pure White & Tight */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; /* தூய வெள்ளை நிறம் */
        margin: 8px 0 0 0 !important; /* இடைவெளி குறைப்பு */
        font-weight: 500;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* Developer - Gold Color & Tight */
    .dev-text {
        font-family: 'Lexend', sans-serif;
        font-size: 16px !important;
        color: #FFD700 !important; /* கண்ணியமான தங்க நிறம் (Gold) */
        margin: 5px 0 0 0 !important; /* இடைவெளி குறைப்பு */
        font-weight: 600;
        opacity: 0.9;
    }

    /* Mobile Responsive Logic */
    @media (max-width: 768px) {
        .header-container { gap: 15px; padding: 15px; }
        .logo-img { width: 100px !important; margin-top: 5px; }
        .main-title { font-size: 28px !important; line-height: 0.9 !important; }
        .main-tagline { font-size: 14px !important; }
    }

    /* Chat Button Styling */
    .stButton > button {
        height: 65px !important;
        border-radius: 12px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Assets & Display ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

if b64_img:
    st.markdown(f'''
        <div class="header-container">
            <img src="data:image/png;base64,{b64_img}" class="logo-img">
            <div class="content-box">
                <h1 class="main-title">AI SMART MENTOR</h1>
                <p class="main-tagline">"Everyone has the right to education"</p>
                <p class="dev-text">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🧠 4. AI Logic (Strict Evaluation Mode) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def ai_response(q, pdf=""):
    try:
        sys_msg = "You are AI Smart Mentor, a professional Educational Assistant developed by Brammadevan. Be factual. Temperature: 0.0."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf[:1500]}\n" if pdf else ""
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 🎙️ 5. Interaction UI ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF கோப்புகளை இங்கே பதிவேற்றலாம்", type=["pdf"])
pdf_txt = ""
if up_pdf:
    doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
    pdf_txt = "".join([p.get_text() for p in doc])
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", language='ta-IN', use_container_width=True, key='mic_final_v50')
t_in = st.chat_input("கல்வி தொடர்பான கேள்விகளைக் கேட்கவும்...")
prompt = v_in if v_in else t_in

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            rep = ai_response(prompt, pdf_txt)
            st.markdown(rep)
            try:
                is_ta = bool(re.search(r'[\u0b80-\u0bff]', rep))
                tts = gTTS(text=rep[:300], lang='ta' if is_ta else 'en')
                tts.save("res.mp3")
                st.audio("res.mp3", autoplay=True)
            except: pass
    st.session_state.messages.append({"role": "assistant", "content": rep})
