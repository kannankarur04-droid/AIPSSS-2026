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

# --- 🎨 2. Styling (CSS) - Compact & Large Logo ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Container */
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 25px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.03); 
        padding: 15px;
        border-radius: 20px;
    }

    /* லோகோ அளவு - இப்போது மிகப்பரிதாக (350px) */
    .main-logo {
        width: 350px !important; 
        max-width: 350px !important;
        height: auto;
        object-fit: contain;
    }

    /* டெக்ஸ்ட் பாக்ஸ் - இடைவெளி குறைப்பு */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    .main-title {
        font-size: 4.5rem !important; /* அளவை சற்று குறைத்துள்ளேன் */
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; /* வரிகளுக்கு இடையே மிகக் குறைந்த இடைவெளி */
        letter-spacing: -2px;
    }

    .subtitle {
        font-size: 1.5rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.0 !important;
        padding-top: 10px;
        white-space: nowrap;
    }

    .quote-text {
        font-size: 1.1rem !important;
        font-style: italic !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        line-height: 1.0 !important;
        padding-top: 5px;
    }

    .developer {
        font-size: 1rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        line-height: 1.0 !important;
        padding-top: 5px;
        opacity: 0.8;
    }

    /* மொபைல் வியூ - லோகோ மற்றும் டெக்ஸ்ட் அலைன்மென்ட் */
    @media (max-width: 768px) {
        .aipsss-header { flex-direction: column; text-align: center; gap: 10px; padding: 10px; }
        .main-logo { width: 150px !important; }
        .main-title { font-size: 2.8rem !important; }
        .subtitle { font-size: 0.9rem !important; white-space: normal; }
        .quote-text, .developer { font-size: 0.8rem !important; }
    }

    .stButton > button { height: 65px !important; border-radius: 12px !important; background-color: #FF4B4B !important; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

if b64_img:
    st.markdown(f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{b64_img}" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(q, pdf=""):
    try:
        forbidden = ["game", "gaming", "cheat", "hack", "illegal", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(w in q.lower() for w in forbidden):
            return "மன்னிக்கவும், நான் கல்வி தொடர்பான உதவிகளை மட்டுமே வழங்க முடியும்."
        
        sys_msg = "You are AIPSSS, a professional Education Mentor. Answer educational queries only."
        hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        ctx = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        
        msgs = [{"role": "system", "content": sys_msg}] + hist + [{"role": "user", "content": ctx + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.1)
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])
pdf_txt = ""
if up_pdf:
    with st.spinner("Reading PDF..."):
        doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
        pdf_txt = "".join([p.get_text() for p in doc])
    st.success(f"✅ '{up_pdf.name}' Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_v31')
t_in = st.chat_input("கேள்வியைக் கேட்கவும்...")
prompt = v_in if v_in else t_in

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            rep = ai_response(prompt, pdf_txt)
            st.markdown(rep)
            try:
                is_ta = bool(re.search(r'[\u0b80-\u0bff]', rep))
                tts = gTTS(text=rep[:300], lang='ta' if is_ta else 'en')
                tts.save("res.mp3")
                st.audio("res.mp3", autoplay=True)
            except: pass
    st.session_state.messages.append({"role": "assistant", "content": rep})
