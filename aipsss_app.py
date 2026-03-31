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

# --- 🎨 2. Styling (CSS) - நீங்கள் கொடுத்த புதிய ஸ்டைல் ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* பொதுவான அமைப்பு (கணினிக்காக) */
    .aipsss-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px; /* லோகோ மற்றும் டெக்ஸ்ட் இடைவெளி */
        padding: 20px;
        flex-wrap: wrap; /* மொபைலில் தானாக கீழே வர உதவும் */
        margin-top: 20px;
        margin-bottom: 30px;
    }

    /* லோகோ அளவு */
    .main-logo {
        width: 200px; /* கணினியில் லோகோவின் அளவு */
        height: auto;
        transition: 0.3s;
    }

    .content-box {
        text-align: left;
    }

    .main-title {
        font-size: 4.5rem !important; /* தலைப்பு இன்னும் பெரிதாக */
        color: #ff4d4d !important; /* சிகப்பு நிறம் */
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.9 !important;
    }

    .subtitle {
        font-size: 1.5rem !important;
        color: #FFD700 !important; /* தங்க நிறம் */
        margin: 5px 0 !important;
        font-weight: bold !important;
    }

    .tagline {
        font-style: italic !important;
        color: #FFD700 !important; /* தங்க நிறம் */
        margin-top: 10px !important;
        font-weight: 500 !important;
    }

    .developer {
        font-size: 1rem !important;
        color: #FFFFFF !important; /* வெள்ளை நிறம் */
        opacity: 0.9 !important;
        margin-top: 5px !important;
    }

    /* மொபைல் போன்களுக்கான மாற்றம் (Screen size < 768px) */
    @media (max-width: 768px) {
        .aipsss-header {
            flex-direction: column; /* லோகோ மேலே, டெக்ஸ்ட் கீழே */
            text-align: center;
            gap: 15px;
        }

        .content-box {
            text-align: center; /* மொபைலில் நடுவில் வர */
        }

        .main-logo {
            width: 120px; /* மொபைலில் லோகோவின் அளவு */
        }

        .main-title {
            font-size: 3rem !important;
        }

        .subtitle {
            font-size: 1.2rem !important;
        }
    }

    /* Chat & Button Styles */
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic (HTML Integration) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    # நீங்கள் கொடுத்த HTML கட்டமைப்பு
    header_html = f'''
        <div class="aipsss-header">
            <div class="logo-box">
                <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            </div>
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B; text-align:center;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 5. AI Core Logic (Security & Education Focus) ---
def ai_response(user_query, pdf_text=""):
    try:
        # 🚫 பாதுகாப்பு விதிமுறைகள்
        restricted = ["cinema", "movie", "actor", "actress", "song", "adult", "porn", "violence", "illegal", "hack", "சினிமா", "படம்", "நடிகர்", "பாடல்", "ஆபாசம்"]
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும், AIPSSS ஒரு கல்வி மற்றும் வேலைவாய்ப்பு சார்ந்த தளம் மட்டுமே. தேவையற்ற தகவல்களை என்னால் வழங்க முடியாது."

        system_instruction = """
        You are AIPSSS, a dedicated Educational and Career Mentor. 
        - Provide help ONLY for Education, Career, Skills, and Exams.
        - Tone: Encouraging, Clear, and Professional.
        - If query is non-educational, politely decline.
        """

        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI & Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_mic_v3')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேட", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF இணைக்கப்பட்டது!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            try:
                is_tamil = bool(
