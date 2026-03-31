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

# --- 🎨 2. Styling (Desktop & Mobile Side-by-Side Fix) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; max-width: 1300px; }
    
    /* Header Container - Force Side-by-Side on all screens */
    .aipsss-header {
        display: flex;
        flex-direction: row; /* எப்போதும் பக்கவாட்டில் இருக்க */
        align-items: center; 
        justify-content: flex-start;
        gap: 15px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 15px;
        border-radius: 20px;
        flex-wrap: nowrap; /* அடுத்த வரிக்குச் செல்லாமல் தடுக்க */
    }

    /* Logo Styling */
    .main-logo {
        height: auto;
        width: 300px !important; /* கம்ப்யூட்டரில் அகலம் */
        max-height: 250px;
        object-fit: contain;
        flex-shrink: 0; /* லோகோ சுருங்காமல் இருக்க */
    }

    /* Content Box - No Extra Spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
        overflow: hidden;
    }

    .main-title {
        font-size: 4.5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 950 !important;
        line-height: 0.8 !important;
        letter-spacing: -2px;
    }

    .subtitle {
        font-size: 1.5rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        padding-top: 8px;
        white-space: nowrap; /* ஒரே வரியில் இருக்க */
    }

    .quote-text {
        font-size: 1.1rem !important;
        font-style: italic !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        padding-top: 4px;
        white-space: nowrap;
    }

    .developer {
        font-size: 1rem !important;
        color: #FFFFFF !important; 
        margin: 0 !important;
        padding-top: 4px;
        opacity: 0.9;
    }

    /* Mobile Responsive - Strict Side-by-Side */
    @media (max-width: 768px) {
        .aipsss-header { 
            gap: 10px; 
            padding: 10px;
            margin-top: 10px;
        }
        .main-logo { 
            width: 100px !important; /* மொபைலில் லோகோவின் அகலம் குறைக்கப்பட்டுள்ளது */
            height: auto !important;
        }
        .main-title { font-size: 2.2rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.8rem !important; padding-top: 4px; }
        .quote-text { font-size: 0.7rem !important; }
        .developer { font-size: 0.7rem !important; }
        .content-box { gap: 2px; }
    }

    .stButton > button { height: 60px !important; border-radius: 12px !important; background-color: #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
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

# --- 🧠 5. AI Engine (Strict Filter) ---
def ai_response(q, pdf=""):
    try:
        forbidden = ["game", "gaming", "play", "pubg", "cheat", "hack", "movie", "cinema", "song", "விளையாட்டு", "சினிமா"]
        if any(w in q.lower() for w in forbidden):
            return "மன்னிக்கவும் பிரம்மதேவன், நான் கல்வி மற்றும் வேலைவாய்ப்பு வழிகாட்டி மட்டுமே. விளையாட்டு அல்லது பொழுதுபோக்கு தொடர்பான தகவல்களைத் தவிர்க்கவும்."

        sys_msg = "You are AIPSSS, an Education Mentor developed by Brammadevan. Answer ONLY educational queries. No games."
        hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        ctx = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        
        msgs = [{"role": "system", "content": sys_msg}] + hist + [{"role": "user", "content": ctx + q}]
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

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_side_v1')
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
