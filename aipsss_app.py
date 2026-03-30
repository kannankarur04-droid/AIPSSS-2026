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

# --- 🎨 2. Styling (CSS) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    
    /* லோகோ மற்றும் பெயருக்கான பெட்டி */
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 20px;
    }

    /* லோகோ அளவு - சிறியதாக (100px) */
    .logo-img {
        width: 100px;
        height: auto;
    }

    /* படத்தின் கீழ் உங்கள் பெயர் */
    .logo-caption {
        font-size: 13px;
        color: #666;
        margin-top: 5px;
        font-weight: bold;
    }

    /* AIPSSS தலைப்பு */
    .main-title { 
        font-size: 45px !important; 
        font-weight: 900; 
        text-align: center; 
        color: #FF4B4B;
        margin: 0;
        line-height: 1.1;
    }
    
    .main-tagline {
        font-size: 16px !important; 
        text-align: center; 
        color: #555;
        margin-top: 2px;
        font-weight: bold;
    }
    
    /* மைக் பட்டன் ஸ்டைல் */
    .stButton > button {
        height: 80px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
    }

    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Logic (Way 2: Base64) ---
img_name = 'aipsss_robot_final.png' 

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

encoded_img = get_base64_image(img_name)

if encoded_img:
    st.markdown(f'''
        <div class="logo-container">
            <img src="data:image/png;base64,{encoded_img}" class="logo-img">
            <p class="logo-caption">Developed by Kannan</p>
            <p class="main-title">AIPSSS</p>
            <p class="main-tagline">AI Powered Student Support System</p>
        </div>
    ''', unsafe_allow_html=True)
else:
    # படம் இல்லையென்றால் வெறும் எழுத்துக்கள் மட்டும் வரும்
    st.markdown('''
        <div class="logo-container">
            <p class="main-title">AIPSSS</p>
            <p class="main-tagline">AI Powered Student Support System</p>
            <p style="color:red; font-size:10px;">(Logo file not found in root folder)</p>
        </div>
    ''', unsafe_allow_html=True)

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
                {"role": "system", "content": "You are AIPSSS, a helpful educational assistant. Answer clearly in Tamil or English."},
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
            
            # ஆடியோ பதில்
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
