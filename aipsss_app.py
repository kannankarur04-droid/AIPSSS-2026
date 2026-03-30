import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Vertical Alignment Fix ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    
    /* லோகோ மற்றும் பெயரை செங்குத்தாக நடுவில் வைக்க (Vertical Center) */
    [data-testid="stHorizontalBlock"] {
        align-items: center; 
        display: flex;
        gap: 15px;
        margin-top: -35px;
    }

    /* AIPSSS Title */
    .main-title { 
        font-size: 48px !important; 
        font-weight: 900; 
        color: #FF4B4B;
        margin: 0;
        line-height: 1.1;
    }
    
    /* Tagline - Gold Color */
    .main-tagline {
        font-size: 17px !important; 
        color: #FFD700; 
        font-weight: bold;
        margin: 0;
        display: block;
    }
    
    /* Mic Button */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }

    /* PDF Uploader */
    .stFileUploader { margin-top: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Alignment (Logo Left, Text Right) ---
logo_path = os.path.join(os.path.dirname(__file__), 'aipsss_robot.png')

try:
    if os.path.exists(logo_path):
        col1, col2 = st.columns([1, 4]) 
        with col1:
            st.image(Image.open(logo_path), width=85) 
        with col2:
            st.markdown('<p class="main-title">AIPSSS</p>', unsafe_allow_html=True)
            st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)
except:
    st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 4. AI Logic (Strict Accuracy Rule Added) ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        
        # 'System' மெசேஜில் துல்லியம் குறித்த கட்டளை சேர்க்கப்பட்டுள்ளது
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """You are AIPSSS, a highly accurate Education Assistant. 
                    CRITICAL RULE: Accuracy is paramount as students use this for learning. 
                    Double-check all numbers, translations, and facts (especially Tamil number names like 90 = Thonnooru). 
                    Keep answers within 4 lines and be encouraging."""
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1 # பதில்கள் மாறாமல் துல்லியமாக இருக்க குறைந்த டெம்பரேச்சர்
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 5. Voice Input ---
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_final_mic')

# --- 🚀 6. Process Input ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 💬 7. Output ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("துல்லியமாகச் சரிபார்க்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("r.mp3")
            st.audio("r.mp3", autoplay=True)
