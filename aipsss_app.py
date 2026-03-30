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

# --- 🎨 2. Styling (Clean & Modern) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    
    /* 🎓 AIPSSS - Bold Red */
    .main-title { 
        font-size: 52px !important; 
        font-weight: 900; 
        text-align: center; 
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    
    /* Tagline - Simple & Clear */
    .main-tagline {
        font-size: 18px !important; 
        text-align: center; 
        color: #555;
        margin-bottom: 30px;
        display: block;
        font-style: italic;
    }
    
    /* Mic Button */
    .stButton > button {
        height: 90px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 24px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
    }

    /* PDF Uploader Box */
    .stFileUploader { margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header ---
st.markdown('<p class="main-title">🎓 AIPSSS</p>', unsafe_allow_html=True)
st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)

# --- 🎙️ 4. Voice Input (Top) ---
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

# --- ⌨️ 6. Text Input & PDF (The Order You Asked) ---
# முதலில் கேள்வி கேட்கும் பெட்டி
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# அதன் பிறகு PDF அப்லோடர் (கண்டிப்பாக கீழே இருக்கும்)
st.write("---") # ஒரு சிறிய கோடு பிரிப்பிற்காக
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF-ஐ இங்கே பதிவேற்றவும்)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 🚀 7. Output ---
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
