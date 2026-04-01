import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image
import fitz  # PyMuPDF
import base64

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Mobile Friendly & Responsive ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* AIPSSS Title Style - Fixed Clipping */
    .main-title { 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B;
        letter-spacing: 1px;
        margin: 0 !important; 
        display: block !important;
        overflow: visible !important; /* வெட்டப்படுவதைத் தவிர்க்க */
    }

    /* Responsive Sizes */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 32px !important; line-height: 1.3 !important; }
        .main-tagline { font-size: 12px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 52px !important; line-height: 1.5 !important; }
        .main-tagline { font-size: 16px !important; }
    }
    
    .main-tagline {
        text-align: left; 
        color: #555; 
        margin-top: 0px !important;
        line-height: 1.2 !important;
        font-weight: bold;
        display: block;
    }
    
    /* Button Style */
    .stButton > button {
        height: 75px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic (Fixed Alignment & Clipping) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        # HTML Flexbox - தலைப்பு மேலே ஏறாமல் இருக்க margin-top: 0px
        header_html = f'''
            <div style="display: flex; align-items: center; gap: 15px; margin-top: 0px; margin-bottom: 25px; padding-top: 5px;">
                <img src="data:image/png;base64,{base64_img}" style="width: 70px; height: auto; object-fit: contain;">
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <p class="main-title">AIPSSS</p>
                    <p class="main-tagline">AI Powered Student Support System</p>
                </div>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="color:#FF4B4B; margin:0;">AIPSSS</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#555; font-weight:bold; margin:0;">AI Powered Student Support System</p>', unsafe_allow_html=True)
except Exception:
    st.markdown('<h1 style="color:#FF4B4B; margin:0;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic_v2'
)

# --- 🧠 5. AI Core Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AIPSSS, a helpful Education Assistant."},
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
            st.success(reply)
            
            # Audio Output
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
