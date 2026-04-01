import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF
import base64

# --- 🔐 1. API அமைப்பு ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("GROQ_API_KEY இல்லை! தயவுசெய்து Secrets-ல் சரிபார்க்கவும்.")
    st.stop()

# --- 🎨 2. டிசைன் மற்றும் லேஅவுட் (Kannan's Gentle View) ---
st.set_page_config(page_title="AI Smart Mentor", layout="wide", page_icon="🤖🎓")

# நவீன Lexend ஃபான்ட் மற்றும் கச்சிதமான CSS அலைன்மென்ட்
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .block-container { padding-top: 1.5rem !important; max-width: 1300px; }
    
    /* ஹெட்டர் கண்டெய்னர் */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 40px; 
        margin-bottom: 35px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 30px 45px;
        border-radius: 20px;
        flex-wrap: nowrap;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Lexend', sans-serif;
    }

    /* லோகோ - பெரிய அளவில் */
    .main-logo {
        height: auto;
        width: 320px !important; 
        max-height: 250px;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* எழுத்துக்கள் இருக்கும் பெட்டி */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* AI Smart Mentor - ஒரே வரியில் கச்சிதமாக */
    .main-title {
        font-size: 3.8rem !important; 
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.9 !important;
        letter-spacing: -2px;
        white-space: nowrap;
    }

    /* பொன்மொழி - தங்கம் மற்றும் வெள்ளை கலவையில் */
    .quote-text {
        font-size: 1.5rem !important;
        color: #FFD700 !important; 
        margin: 0 !important;
        font-weight: 500 !important;
        line-height: 1.1 !important;
        padding-top: 10px;
        font-style: italic;
    }

    /* டெவலப்பர் பெயர் */
    .developer {
        font-size: 1.1rem !important;
        color: #ffffff !important; 
        margin: 0 !important;
        padding-top: 5px;
        opacity: 0.8;
    }

    /* மொபைல் போன் வியூ - Responsive */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 15px; }
        .main-logo { width: 100px !important; }
        .main-title { font-size: 1.8rem !important; letter-spacing: -1px; }
        .quote-text { font-size: 0.8rem !important; padding-top: 5px; }
        .developer { font-size: 0.75rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. மெமரி மேனேஜ்மென்ட் ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# லோகோ கோப்பினைப் பதிவேற்றுதல்
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

b64_img = get_base64_image(img_path)

# --- 🖼️ 4. ஹெட்டர் திரையில் காட்டுதல் ---
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

# --- 🤖 5. AI இன்ஜின் (துல்லியமான பதில்களுக்கு) ---
def ai_response(q, pdf=""):
    try:
        sys_msg = """
        ROLE: You are AI Smart Mentor, a professional Educational Assistant developed by Brammadevan.
        CORE PRINCIPLE: Clear Subject Separation. 
        - If the user asks about Auditing, provide technical commerce definitions.
        - If the user asks about a student's personal responsibilities, answer based on ethics and study habits.
        - DO NOT mix subjects. Temperature: 0.0.
        """
        # முந்தைய 3 உரையாடல்களை மட்டும் நினைவில் கொள்ளும் (குழப்பத்தைத் தவிர்க்க)
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf[:1200]}\n" if pdf else ""
        
        msgs = [{"role": "system", "content": sys_msg}] + history + [{"role": "user", "content": context + q}]
        
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, temperature=0.0)
        return res.choices[0].message.content
    except Exception as e:
        return f"AI பிழை: {str(e)}"

# --- 🎙️ 6. பயனர் இடைமுகம் (Interaction) ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

up_pdf = st.file_uploader("📂 PDF கோப்புகளை இங்கே பதிவேற்றலாம்", type=["pdf"])
pdf_txt = ""
if up_pdf:
    doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
    pdf_txt = "".join([p.get_text() for p in doc])
    st.success("✅ PDF தயாராக உள்ளது!")

# வாய்ஸ் மற்றும் டெக்ஸ்ட் இன்புட்
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
