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

# --- 🎨 2. Styling (Mobile Top Fix & Spacing) ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; max-width: 1300px; }
    
    /* Header Container */
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 30px; 
        margin-bottom: 35px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo Styling - Fixed for Mobile Head-cut */
    .main-logo {
        height: 250px !important;
        width: auto !important;
        object-fit: contain;
        display: block;
        margin-top: 10px; /* மேலே தலை வெட்டப்படாமல் இருக்க இடைவெளி */
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
        line-height: 0.9 !important;
    }

    .subtitle {
        font-size: 1.7rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        padding-top: 12px;
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

    /* Mobile View Responsive */
    @media (max-width: 768px) {
        .aipsss-header { 
            flex-direction: column; 
            text-align: center; 
            gap: 15px; 
            padding: 20px 10px;
            margin-top: 30px;
        }
        .main-logo { 
            height: 160px !important; 
            width: auto !important;
            margin: 0 auto;
        }
        .main-title { font-size: 3rem !important; line-height: 1.0 !important; }
        .subtitle { font-size: 1.1rem !important; white-space: normal; line-height: 1.2 !important; }
    }

    .stButton > button { height: 70px !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
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

# --- 🧠 5. AI Logic (The Guardian Filter) ---
def ai_response(q, pdf=""):
    try:
        # Keywords to strictly block
        restricted_topics = [
            "game", "gaming", "play", "pubg", "cheat", "hack", "illegal", "movie", "cinema", "song", "actor", 
            "விளையாட்டு", "சினிமா", "பாடல்", "படம்", "கேம்"
        ]
        
        if any(word in q.lower() for word in restricted_topics):
            return "மன்னிக்கவும் பிரம்மதேவன், நான் ஒரு கல்வி மற்றும் வேலைவாய்ப்பு வழிகாட்டி (Education Mentor) மட்டுமே. விளையாட்டு, சினிமா அல்லது பொழுதுபோக்கு சார்ந்த கேள்விகளுக்கு என்னால் பதில் அளிக்க முடியாது. கல்வி தொடர்பாக ஏதேனும் உதவி தேவையா?"

        # System Instruction - No Hallucination, Strictly Education
        sys_msg = """
        ROLE: You are AIPSSS, a professional Education and Career Mentor developed by Brammadevan.
        STRICT RULE 1: ONLY answer questions related to Education, Competitive Exams, Job guidance, and Skills.
        STRICT RULE 2: NEVER talk about mobile games, video games, or entertainment. 
        STRICT RULE 3: If a user asks about non-educational topics, politely refuse.
        STRICT RULE 4: DO NOT hallucinate or give wrong info about brands.
        TONE: Helpful, natural, and direct.
        """
        
        hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        ctx = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        
        msgs = [{"role": "system", "content": sys_msg}] + hist + [{"role": "user", "content": ctx + q}]
        
        # Temperature set to 0.0 for zero hallucination
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
    with st.spinner("PDF Reading..."):
        doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
        pdf_txt = "".join([p.get_text() for p in doc])
    st.success(f"✅ PDF Ready!")

v_in = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_guard_v40')
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
