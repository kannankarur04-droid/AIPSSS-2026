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

# --- 🎨 2. Styling (CSS) - Modern & Gentle View ---
st.set_page_config(page_title="AI Smart Mentor", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* Title Style - CAPITAL & BOLD */
    .main-title { 
        font-weight: 900; 
        color: #FF4B4B;
        text-transform: uppercase;
        margin: 0 !important; 
        line-height: 1.0 !important;
        letter-spacing: -1px;
    }

    /* Tagline - White Color */
    .main-tagline {
        color: #FFFFFF !important; 
        margin-top: 5px !important;
        font-weight: 500;
        font-style: italic;
        line-height: 1.1 !important;
    }

    /* Developer - Gold Color */
    .dev-text {
        color: #FFD700 !important; 
        font-weight: 600;
        margin-top: 3px !important;
        font-size: 14px;
    }

    /* Responsive Logic */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 28px !important; }
        .main-tagline { font-size: 13px !important; }
        .logo-img { width: 90px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 46px !important; }
        .main-tagline { font-size: 18px !important; }
        .logo-img { width: 150px !important; } /* லோகோ பெரிதாக்கப்பட்டுள்ளது */
    }
    
    /* Chat & Button UI */
    .stButton > button {
        height: 65px !important;
        border-radius: 12px !important;
        background-color: #FF4B4B !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

try:
    b64_img = get_base64_image(img_path)
    if b64_img:
        header_html = f'''
            <div style="display: flex; align-items: center; gap: 25px; margin-bottom: 30px;">
                <img src="data:image/png;base64,{b64_img}" class="logo-img" style="height: auto; object-fit: contain;">
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <p class="main-title">AI SMART MENTOR</p>
                    <p class="main-tagline">"Everyone has the right to education"</p>
                    <p class="dev-text">Developed by Brammadevan</p>
                </div>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
except Exception:
    st.markdown('<h1 style="color:#FF4B4B;">AI SMART MENTOR</h1>', unsafe_allow_html=True)

# --- 🤖 4. AI Engine (Strict Evaluation Mode) ---
def ai_response(q, pdf_text=""):
    try:
        # 0.0 Temperature for Accuracy
        sys_msg = "You are AI Smart Mentor, a professional Education Expert. Be factual. No Hallucination. Temp: 0.0."
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.0
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction UI ---
v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", language='ta-IN', use_container_width=True, key='mic_v4')
t_in = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
up_pdf = st.file_uploader("📂 PDF கோப்புகள் (தேவைப்பட்டால்)", type=["pdf"])

pdf_context = ""
if up_pdf:
    doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
    pdf_context = "".join([p.get_text() for p in doc])
    st.success("✅ PDF இணைக்கப்பட்டது!")

# --- 🚀 6. Execution ---
prompt = v_in if v_in else t_in

if prompt:
    with st.chat_message("user"): st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            try:
                is_ta = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_ta else 'en')
                tts.save("res.mp3")
                st.audio("res.mp3", autoplay=True)
            except: pass
