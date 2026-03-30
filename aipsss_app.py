import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import base64
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Fix for Half Display ---
st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    
    /* லோகோ மற்றும் பெயருக்கான கண்டெய்னர் */
    .header-wrapper {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        margin-top: -20px;
        margin-bottom: 25px;
        gap: 15px;
        min-height: 120px; /* படத்திற்குத் தேவையான குறைந்தபட்ச உயரம் */
    }

    /* லோகோ முழுமையாகத் தெரிய height: auto மற்றும் display: block */
    .logo-img {
        width: 120px;
        height: auto !important; /* உயரத்தை கட்டாயமாக தானாகச் சரிசெய்யும் */
        display: block;
        object-fit: contain;
    }

    .text-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
    }

    .main-title { 
        font-size: 45px !important; 
        font-weight: 900; 
        color: #FF4B4B;
        margin: 0;
        line-height: 1.1;
    }
    
    .main-tagline {
        font-size: 16px !important; 
        color: #555;
        margin-top: 2px;
        font-weight: bold;
    }

    /* Developed by Kannan - Right Bottom of Logo */
    .logo-caption {
        font-size: 11px;
        color: #888;
        text-align: right;
        margin-top: 2px;
        width: 120px; /* படத்தின் அதே அகலம் */
    }
    
    .stButton > button {
        height: 80px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        background-color: #FF4B4B !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Logic (Base64) ---
img_name = 'aipsss_robot_final.png' 

def get_base64_image(path):
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

encoded_img = get_base64_image(img_name)

if encoded_img:
    st.markdown(f'''
        <div class="header-wrapper">
            <div style="display: flex; flex-direction: column;">
                <img src="data:image/png;base64,{encoded_img}" class="logo-img">
                <p class="logo-caption">Developed by Kannan</p>
            </div>
            <div class="text-container">
                <p class="main-title">AIPSSS</p>
                <p class="main-tagline">AI Powered Student Support System</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Voice Input ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic'
)

# --- 🧠 5. AI Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AIPSSS, a helpful educational assistant. Answer in Tamil or English."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- ⌨️ 6. Input & PDF ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

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
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.write(reply)
            
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
