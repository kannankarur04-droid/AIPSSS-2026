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

# --- 🎨 2. UI/UX Design (The CSS Fix) ---
st.set_page_config(page_title="AI Smart Mentor", layout="wide", page_icon="🤖🎓")

# இந்த ஒரு ப்ளாக் (Block) தான் அந்த எழுத்துக்களை டிசைனாக மாற்றும்
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    /* முழுத் திரையின் பின்புலம் */
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem !important; max-width: 1300px; }
    
    /* ஹெட்டர் பெட்டி - நவீன டிசைன் */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 40px; 
        margin-bottom: 35px;
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.2), rgba(30, 58, 138, 0.1));
        padding: 30px 45px;
        border-radius: 20px;
        flex-wrap: nowrap;
        border: 1px solid rgba(59, 130, 246, 0.3);
        font-family: 'Lexend', sans-serif;
    }

    .main-logo {
        height: auto;
        width: 280px !important; 
        max-height: 220px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* AI Smart Mentor - Soft Blue */
    .main-title {
        font-size: 3.8rem !important; 
        color: #60a5fa !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.9 !important;
        letter-spacing: -2px;
        white-space: nowrap;
    }

    /* பொன்மொழி - Creamy White */
    .quote-text {
        font-size: 1.5rem !important;
        color: #e5e7eb !important; 
        margin: 0 !important;
        font-weight: 400 !important;
        line-height: 1.1 !important;
        padding-top: 10px;
        font-style: italic;
    }

    /* டெவலப்பர் - Soft Gold */
    .developer {
        font-size: 1.1rem !important;
        color: #fbbf24 !important; 
        margin: 0 !important;
        padding-top: 5px;
        font-weight: 600;
        opacity: 0.9;
    }

    /* Mobile View Optimization */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 15px; }
        .main-logo { width: 90px !important; }
        .main-title { font-size: 1.8rem !important; letter-spacing: -1px; }
        .quote-text { font-size: 0.8rem !important; padding-top: 5px; }
        .developer { font-size: 0.75rem !important; }
    }
    </style>
    """, unsafe_allow_html=True) # இந்த வரிதான் மிக முக்கியம்

# --- 🧠 3. Logic & Assets ---
if "messages" not in st.session_state:
    st.session_state.messages = []

img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

# --- 🖼️ 4. Header Display ---
if b64_img:
    st.markdown(f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{b64_img}" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI Smart Mentor</h1>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🤖 5. AI Engine ---
def ai_response(q, pdf=""):
    try:
        sys_msg = "You are AI Smart Mentor, a professional Educational Assistant. Temperature: 0.0."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF கோப்புகளை இங்கே பதிவேற்றலாம்", type=["pdf"])
pdf_txt = ""
if up_pdf:
    doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
    pdf_txt = "".join([p.get_text() for p in doc])
    st.success("✅ PDF Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_kannan')
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
