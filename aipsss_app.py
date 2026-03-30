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

# --- 🎨 2. Minimalist UI Styling ---
st.set_page_config(page_title="AIPSSS", layout="centered")

st.markdown("""
    <style>
    /* தலைப்பை மட்டும் பெரியதாகக் காட்ட */
    .main-title { 
        font-size: 40px !important; 
        font-weight: 900; 
        text-align: center; 
        margin-top: -60px; 
        color: #FF4B4B;
        letter-spacing: 2px;
    }
    
    /* மைக் பட்டன் ஸ்டைல் */
    .stButton > button {
        height: 80px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
    }
    
    /* தேவையற்ற இடைவெளிகளைக் குறைக்க */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">AIPSSS</p>', unsafe_allow_html=True)

# --- 🧠 3. Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Info: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are a kind Education Assistant. Answer based on PDF if provided. Be brief (max 4 lines)."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 📁 4. Main Screen Controls ---
uploaded_pdf = st.file_uploader("📂 PDF-ஐ இங்கே பதிவேற்றவும்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF தயார்!")

# --- 🎙️ 5. Interaction ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='final_mic'
)

text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        reply = ai_response(prompt, pdf_context)
        st.success(reply)
        
        # Audio Output
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
        tts = gTTS(text=reply[:250], lang='ta' if is_tamil else 'en')
        tts.save("r.mp3")
        st.audio("r.mp3", autoplay=True)
