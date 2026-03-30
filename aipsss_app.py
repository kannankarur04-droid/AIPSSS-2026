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

# --- 🎨 2. Minimalist & Mobile Friendly CSS ---
st.set_page_config(page_title="AIPSSS", layout="centered")

st.markdown("""
    <style>
    /* மொபைல் திரையில் தேவையற்ற இடைவெளியைக் குறைக்க */
    .block-container { padding-top: 1rem; }
    
    /* மைக் பட்டன் - பெரியதாகவும் சிவப்பு நிறத்திலும் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    
    /* PDF அப்லோடர் பெட்டி */
    .stFileUploader { margin-top: 5px; }
    
    /* தலைப்பு லோகோ இல்லையென்றால் மட்டும் தெரியும் */
    .fallback-title { 
        font-size: 45px; font-weight: 900; text-align: center; 
        color: #FF4B4B; margin-top: -50px; letter-spacing: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Placement (முகப்பில் லோகோ) ---
try:
    # உங்கள் GitHub-ல் aipsss_logo.png என்ற பெயரில் படம் இருக்க வேண்டும்
    logo_path = os.path.join(os.path.dirname(__file__), 'aipsss_logo.png')
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo_img, use_container_width=True)
    else:
        st.markdown('<p class="fallback-title">AIPSSS</p>', unsafe_allow_html=True)
except:
    st.markdown('<p class="fallback-title">AIPSSS</p>', unsafe_allow_html=True)

# --- 🧠 4. AI Core Logic (Groq) ---
def ai_response(q, pdf_text=""):
    try:
        # PDF தகவலை 1500 எழுத்துக்களுக்குள் சுருக்குகிறோம் (Token Safety)
        context = f"PDF Content: {pdf_text[:1500]}" if pdf_text else ""
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": "You are AIPSSS, a kind Education Assistant. Answer educational doubts briefly (max 4 lines). If PDF context is given, use it. Be encouraging to students."
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 📁 5. PDF Upload (Main Screen) ---
uploaded_pdf = st.file_uploader("📂 PDF-ஐ இங்கே பதிவேற்றவும்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF படிக்கப்பட்டது!")

# --- 🎙️ 6. Interaction (Voice & Text) ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_final_mic'
)

text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # Audio Output
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
