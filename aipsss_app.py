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
    st.error("Missing GROQ_API_KEY! Please check your Streamlit secrets.")
    st.stop()

# --- 🎨 2. Styling (CSS) - Professional Designer Layout ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1.5rem !important; }

    /* Header Container - Rectangle Box Size Reduced */
    .aipsss-header {
        display: flex;
        flex-direction: row; 
        align-items: center; 
        justify-content: flex-start;
        gap: 40px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.04); 
        padding: 15px 45px; /* பெட்டியின் உயரத்தைக் குறைக்க 15px */
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Logo - LARGE Logo as requested */
    .main-logo {
        width: 180px !important; 
        height: auto;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* Text Content Box - Lowered for perfect vertical alignment */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-top: 5px; 
    }

    /* AI STUDENT MENTOR - RED Color & Tight Line Space */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 52px !important; 
        color: #FF4B4B !important; /* RED COLOR */
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.85 !important; /* Very Tight Spacing */
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* Tagline - Pure White & Tight */
    .subtitle {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; /* PURE WHITE */
        margin: 8px 0 0 0 !important;
        font-weight: 500;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* Developer - Gold Color & Tight */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 16px !important;
        color: #FFD700 !important; /* GOLD COLOR */
        margin: 5px 0 0 0 !important;
        font-weight: 600;
        opacity: 0.9;
        line-height: 1.0 !important;
    }

    /* Mobile Responsive Logic */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 10px 15px; }
        .main-logo { width: 90px !important; }
        .main-title { font-size: 26px !important; line-height: 0.9 !important; }
        .subtitle { font-size: 13px !important; }
    }

    /* UI Components */
    .stButton > button {
        height: 65px !important;
        border-radius: 12px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Display Logic (Fixed NameError) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI STUDENT MENTOR</h1>
                <p class="subtitle">Everyone has the right to education</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B;">AI STUDENT MENTOR</h1>', unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "play", "pubg", "cheat", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி தொடர்பான வழிகாட்டி மட்டுமே. பொழுதுபோக்கு தொடர்பான தகவல்களை வழங்க முடியாது."

        system_instruction = "You are AI Student Mentor, a professional Education Mentor. Answer precisely. Strictly no gaming/entertainment stuff."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])
pdf_extracted_text = ""

if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ '{uploaded_pdf.name}' Loaded!")

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_v60')
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except: pass
    st.session_state.messages.append({"role": "assistant", "content": reply})
