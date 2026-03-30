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

# --- 🎨 2. Styling (Logo & Title Side-by-Side) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* லோகோ மற்றும் தலைப்பை ஒரே வரிசையில் வைக்க */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px; /* படத்திற்கும் பெயருக்கும் இடைவெளி */
        margin-top: -40px;
        margin-bottom: 5px;
    }

    .main-title { 
        font-size: 45px !important; 
        font-weight: 900; 
        color: #FF4B4B !important;
        margin: 0;
        line-height: 1;
    }
    
    .main-tagline {
        font-size: 16px !important; 
        text-align: center; 
        color: #FFD700 !important;
        margin-bottom: 20px;
        font-weight: bold;
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
        border: none;
    }

    /* PDF Uploader */
    .stFileUploader { margin-top: -15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header: Logo (Left) + AIPSSS (Right) ---
img_path = os.path.join(os.path.dirname(__file__), 'aipsss_robot.png')

if os.path.exists(img_path):
    # லோகோ மற்றும் தலைப்பை ஒரே வரிசையில் காட்ட (CSS Flexbox மூலம்)
    logo_img = Image.open(img_path)
    # படத்தை சிறியதாக மாற்றி தலைப்புக்கு அருகில் வைக்கிறோம்
    col1, col2 = st.columns([1, 3]) 
    
    with col1:
        st.image(logo_img, width=80) # லோகோ அளவு 80px
    with col2:
        st.markdown('<h1 class="main-title">AIPSSS</h1>', unsafe_allow_html=True)
else:
    st.markdown('<p class="main-title" style="text-align:center;">AIPSSS</p>', unsafe_allow_html=True)

st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction ---
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_final_mic')

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
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF தயார்!")

# --- 💬 7. Output ---
prompt = voice_input if voice_input else text_input
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        reply = ai_response(prompt, pdf_context)
        st.success(reply)
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
        tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
        tts.save("r.mp3")
        st.audio("r.mp3", autoplay=True)
