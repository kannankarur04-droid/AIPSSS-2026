import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (Dark Mode & Color Fix) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🎓")

st.markdown("""
    <style>
    /* முழுத் திரையின் பின்னணியையும் வெள்ளையாகவே வைக்க (விருப்பமென்றால்) */
    /* .main { background-color: white !important; } */

    .block-container { padding-top: 1.5rem !important; }
    
    /* 🎓 AIPSSS - Bright Red */
    .main-title { 
        font-size: 48px !important; 
        font-weight: 900; 
        text-align: center; 
        color: #FF4B4B !important;
        margin-bottom: 0px;
    }
    
    /* Tagline - இப்போது இது 'தங்க நிறத்தில்' (Gold) இருக்கும் */
    /* இது கருப்பு மற்றும் வெள்ளை என இரண்டு பின்னணியிலும் மிகத் தெளிவாகத் தெரியும் */
    .main-tagline {
        font-size: 17px !important; 
        text-align: center; 
        color: #FFD700 !important; /* Gold Color */
        margin-bottom: 20px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    /* மைக் பட்டன் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
    }

    /* PDF அப்லோடர் இடைவெளி குறைப்பு */
    .stFileUploader { margin-top: -15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header ---
st.markdown('<p class="main-title">🎓 AIPSSS</p>', unsafe_allow_html=True)
st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)

# --- 🎙️ 4. Voice Input ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_final_mic'
)

# --- 🧠 5. AI Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AIPSSS, a kind Education Assistant. Answer briefly (max 4 lines)."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🚀 6. Process Input ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# PDF அப்லோடர் - இன்புட் பாக்ஸிற்கு மிக நெருக்கமாக மேலே
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF தயார்!")

# --- 💬 7. Display Response ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        reply = ai_response(prompt, pdf_context)
        st.success(reply)
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
        tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
        tts.save("response.mp3")
        st.audio("response.mp3", autoplay=True)
