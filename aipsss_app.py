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

# --- 🎨 2. Styling (Side-by-Side Logo & Text) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
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

    @media (max-width: 768px) {
        .aipsss-header { gap: 12px; padding: 12px; }
        .main-logo { width: 150px !important; }
        .main-title { font-size: 2.3rem !important; }
        .subtitle { font-size: 0.85rem !important; white-space: normal; }
    }

    .stButton > button { height: 65px !important; border-radius: 12px !important; background-color: #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

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

# --- 🧠 5. AI Engine (The Knowledge Hub) ---
def ai_response(q, pdf=""):
    try:
        # Strict Subject-wise Instruction
        sys_msg = """
        ROLE: You are AIPSSS, a professional Education Mentor.
        DEVELOPER: Developed by Brammadevan.
        
        KNOWLEDGE DOMAINS:
        - TAMIL: Accurate grammar (Ilakkanam) and literature.
        - ENGLISH: Mastery in Tenses, Active/Passive Voice, and Vocabulary.
        - MATHS: Step-by-step solutions for Arithmetic, Algebra, and Aptitude.
        - SCIENCE: Clear explanations for Physics, Chemistry, and Biology.
        - SOCIAL SCIENCE: History, Geography, Indian Polity, and Economics.
        - COMMERCE: Strict accuracy in Auditing (Vouching/Verification) and Accountancy.
        - PSYCHOLOGY: Educational psychology and Child Development (TRB/TET).

        RULES:
        1. NO Cinema/Gaming/Entertainment.
        2. NO Hallucination. If unsure, admit it.
        3. TEMPERATURE: 0.0 (Zero creativity, 100% facts).
        """
        
        # Security Filter
        forbidden = ["game", "gaming", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(w in q.lower() for w in forbidden):
            return "மன்னிக்கவும் கண்ணன், நான் கல்வி வழிகாட்டி மட்டுமே. படிப்பு தொடர்பான கேள்விகளைக் கேட்கவும்."

        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
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
    st.success(f"✅ PDF Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_all_subjects_v1')
t_in = st.chat_input("கேள்வியைக் கேட்கவும்...")
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
