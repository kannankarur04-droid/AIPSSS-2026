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

# --- 🎨 2. UI/UX Design (Kannan's Perfect Badge Layout) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Box - Logo on Left, Text on Right */
    .aipsss-header {
        display: flex;
        flex-direction: row; /* லோகோ இடது, எழுத்து வலது */
        align-items: center; 
        justify-content: flex-start;
        gap: 30px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.07); 
        padding: 30px 40px;
        border-radius: 20px;
        flex-wrap: nowrap; /* அடுத்த வரிக்குச் செல்லாமல் தடுக்க */
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo - Left Side */
    .main-logo {
        height: auto;
        width: 320px !important; 
        max-height: 280px;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* Content Box - Right Side Typography */
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
        line-height: 0.8 !important; /* லைன் ஸ்பேஸ் குறைக்கப்பட்டுள்ளது */
        letter-spacing: -3px;
    }

    .subtitle {
        font-size: 1.8rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.1 !important; /* லைன் ஸ்பேஸ் குறைக்கப்பட்டுள்ளது */
        padding-top: 10px;
    }

    .quote-text {
        font-size: 1.2rem !important;
        font-style: italic !important;
        color: #ffffff !important; 
        margin: 0 !important;
        padding-top: 5px; /* இடைவெளி குறைப்பு */
        opacity: 0.8;
    }

    .developer {
        font-size: 1.1rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 3px;
        font-weight: 600;
    }

    /* Mobile Responsive - No-Wrap Fix */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 15px; }
        .main-logo { width: 110px !important; }
        .main-title { font-size: 2.3rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.8rem !important; padding-top: 5px; white-space: normal; }
        .quote-text, .developer { font-size: 0.65rem !important; }
    }

    .stButton > button { height: 65px !important; border-radius: 12px !important; background-color: #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
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
                <p class="developer">Developed by KANNAN (Brammadevan)</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🧠 5. AI Response (All Subjects) ---
def ai_response(q, pdf=""):
    try:
        sys_msg = """
        ROLE: You are AIPSSS, a professional Educational Mentor.
        KNOWLEDGE: All school subjects (Tamil, English, Maths, Science, Social Studies), Commerce, Auditing, and Psychology.
        RULES: No Hallucination. Be factually correct. No Games/Cinema. Temperature: 0.0.
        """
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])
pdf_txt = ""
if up_pdf:
    with st.spinner("Reading PDF..."):
        doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
        pdf_txt = "".join([p.get_text() for p in doc])
    st.success(f"✅ PDF Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_custom_final_v11')
t_in = st.chat_input("கல்வி தொடர்பான கேள்வியைக் கேட்கவும்...")
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
