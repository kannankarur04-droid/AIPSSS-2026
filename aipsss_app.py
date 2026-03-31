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

# --- 🎨 2. Styling (Logo & Alignment Fix) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Container - Side-by-Side */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 20px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px;
        border-radius: 25px;
        flex-wrap: nowrap;
    }

    /* Logo Size - डेस्कटॉप */
    .main-logo {
        height: auto;
        width: 380px !important; 
        max-height: 280px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
        overflow: hidden;
    }

    .main-title {
        font-size: 5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 0.8 !important;
        letter-spacing: -2px;
    }

    .subtitle {
        font-size: 1.6rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        padding-top: 10px;
    }

    .quote-text {
        font-size: 1.2rem !important;
        font-style: italic !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 5px;
    }

    .developer {
        font-size: 1.1rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        padding-top: 5px;
        opacity: 0.9;
    }

    /* Mobile View */
    @media (max-width: 768px) {
        .aipsss-header { gap: 12px; padding: 12px; }
        .main-logo { width: 150px !important; }
        .main-title { font-size: 2.3rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.85rem !important; white-space: normal; }
        .quote-text, .developer { font-size: 0.75rem !important; white-space: normal; }
    }

    .stButton > button { height: 65px !important; border-radius: 12px !important; background-color: #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic (Syntax Fixed) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(path):
    # இங்கிருந்த பிழை சரி செய்யப்பட்டது
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

# --- 🧠 5. AI Engine (Strict Educational Guardian) ---
def ai_response(q, pdf=""):
    try:
        # 🚫 1. Keywords Filter (Immediate Block)
        forbidden_list = ["game", "gaming", "play", "pubg", "free fire", "cheat", "hack", "illegal", "movie", "cinema", "song", "விளையாட்டு", "சினிமா", "பாடல்", "படம்", "கேம்"]
        
        if any(word in q.lower() for word in forbidden_list):
            return "மன்னிக்கவும் பிரம்மதேவன், நான் ஒரு கல்வி வழிகாட்டி மட்டுமே. விளையாட்டு அல்லது பொழுதுபோக்கு தொடர்பான தகவல்களை என்னால் வழங்க முடியாது. படிப்பு தொடர்பான கேள்விகளை மட்டும் கேட்கவும்."

        # 🎯 2. AI Prompt Constraints
        sys_msg = """
        You are AIPSSS, a professional Education and Career Mentor. 
        Developed by Brammadevan.
        CRITICAL RULES:
        1. Answer ONLY questions related to Education, Jobs, Exams, and Career.
        2. NEVER answer questions about mobile brands for gaming or movies.
        3. If the user asks about non-educational topics, strictly but politely refuse.
        4. Give accurate information only. No hallucinations.
        """
        
        hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        ctx = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        msgs = [{"role": "system", "content": sys_msg}] + hist + [{"role": "user", "content": ctx + q}]
        
        # Temperature 0.0 to ensure zero hallucination
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. Interaction ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])
pdf_txt = ""
if up_pdf:
    with st.spinner("Reading PDF..."):
        doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
        pdf_txt = "".join([p.get_text() for p in doc])
    st.success(f"✅ PDF Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_strict_final')
t_in = st.chat_input("கல்வி தொடர்பான கேள்வியைக் கேட்கவும்...")
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
