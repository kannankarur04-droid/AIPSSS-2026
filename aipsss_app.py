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

# --- 🎨 2. Styling (வெள்ளை இடைவெளியைக் குறைக்க) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🎓")

st.markdown("""
    <style>
    /* திரையின் மேல் மற்றும் கீழ் இடைவெளியைக் குறைக்க */
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 0rem !important; 
    }
    
    /* 🎓 AIPSSS தலைப்பு */
    .main-title { 
        font-size: 48px !important; 
        font-weight: 900; 
        text-align: center; 
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    
    /* Tagline */
    .main-tagline {
        font-size: 16px !important; 
        text-align: center; 
        color: #555;
        margin-bottom: 20px;
        font-style: italic;
    }
    
    /* மைக் பட்டன் - பெரிய அளவு */
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

    /* PDF அப்லோடர் பெட்டி - சுருக்கமான வடிவமைப்பு */
    .stFileUploader { 
        margin-top: -10px !important; 
        padding-bottom: 50px; /* சேட் பாக்ஸிற்கு மேலே நெருக்கமாக வைக்க */
    }
    
    /* சேட் மெசேஜ் பாக்ஸ் இடைவெளியைக் குறைக்க */
    .stChatMessage { margin-bottom: 1px !important; }
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

# --- 🚀 6. Process Input ---
# சேட் இன்புட் எப்போதும் அடியில் இருக்கும்
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# PDF அப்லோடர் - இன்புட் பாக்ஸிற்கு சற்று மேலே நெருக்கமாகத் தெரியும்
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
