import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. API Key Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# --- 🎨 2. Styling (Responsive UI for Desktop & Mobile) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    
    /* லோகோ மற்றும் பெயரை ஒரே வரிசையில் சீராக வைக்க */
    [data-testid="stHorizontalBlock"] {
        align-items: center; 
        display: flex;
        gap: 20px;
        margin-top: -20px;
    }

    /* AIPSSS Title - திரையின் அளவிற்கு ஏற்ப மாறும் (Responsive) */
    .main-title { 
        font-size: clamp(45px, 8vw, 75px) !important; 
        font-weight: 900; 
        color: #FF4B4B !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Tagline - Gold Color */
    .main-tagline {
        font-size: clamp(15px, 3vw, 20px) !important; 
        color: #FFD700 !important;
        font-weight: bold;
        margin-top: 5px;
        display: block;
        letter-spacing: 1px;
    }
    
    /* மைக் பட்டன் - பெரிய அளவு */
    .stButton > button {
        height: 90px !important;
        width: 100% !important;
        border-radius: 18px !important;
        font-size: 24px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
        box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.3);
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        background-color: #FF3333 !important;
    }

    /* PDF Uploader */
    .stFileUploader { margin-top: 15px !important; }
    
    /* Chat Bubbles */
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Construction (Logo Left, Text Right) ---
img_name = 'aipsss_robot.png'
img_path = os.path.join(os.getcwd(), img_name)

try:
    if os.path.exists(img_path):
        # லோகோ மற்றும் பெயருக்கான காலம் (Columns)
        col1, col2 = st.columns([1, 3]) 
        with col1:
            # லோகோ அளவு 120px ஆக அதிகரிக்கப்பட்டுள்ளது (கணினித் திரைக்கு ஏற்றபடி)
            st.image(Image.open(img_path), width=120) 
        with col2:
            st.markdown('<p class="main-title">AIPSSS</p>', unsafe_allow_html=True)
            st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)
    else:
        # படம் இல்லையென்றால்Fallback
        st.markdown('<h1 style="text-align:center; color:#FF4B4B; font-size:60px;">AIPSSS</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold; font-size:20px;">AI Powered Student Support System</p>', unsafe_allow_html=True)
except Exception:
    st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_final_v5'
)

# --- 🧠 5. AI Core Logic (Strict Accuracy Guaranteed) ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """You are AIPSSS, a highly accurate Education Assistant. 
                    Accuracy is your top priority. Students rely on you for learning. 
                    Double-check all facts, translations, and Tamil numbers (e.g., 90 is தொண்ணூறு). 
                    Keep answers encouraging and within 4 lines."""
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🚀 6. Input & PDF Management ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது! இப்போது கேள்வி கேட்கலாம்.")

# --- 💬 7. Display Output ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("துல்லியமாகச் சரிபார்க்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # ஆடியோ பதில் (Audio Response)
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
