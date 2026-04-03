import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF
import base64

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) ---
st.set_page_config(page_title="AI Student Support System", layout="centered", page_icon="🤖")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Header Container */
    .header-container {
        position: relative;
        margin-top: 20px;
        margin-bottom: 50px; /* கீழ் பக்கம் மிதித்து வருவதால் கூடுதல் இடம் */
        width: 100%;
    }

    /* Black Header Banner - செவ்வகக் கட்டம் */
    .header-banner {
        display: flex;
        align-items: center;
        background-color: #000000;
        padding: 25px 25px 25px 180px; /* படத்தின் அளவுக்கு ஏற்ப இடது பக்கம் கேப் */
        border-radius: 12px;
        min-height: 120px;
        position: relative;
        z-index: 1;
    }

    /* Logo Image - பெரிதாக்கப்பட்டு கீழ் விளிம்பை மிதிப்பது போல */
    .logo-img {
        position: absolute;
        bottom: -25px; /* கட்டத்தின் கீழ் விளிம்பைத் தாண்டி மிதிக்க (Overlap) */
        left: 15px; 
        width: 150px; /* லோகோ பெரிதாக்கப்பட்டுள்ளது */
        height: auto;
        z-index: 10; /* கட்டத்திற்கு மேல் தெரிய */
        filter: drop-shadow(0px 5px 10px rgba(0,0,0,0.5));
    }

    /* Text Column */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .main-title { 
        font-size: 32px !important; 
        font-weight: 900; 
        color: #FF4B4B; 
        margin: 0 !important;
        line-height: 1 !important;
    }

    .main-tagline {
        font-size: 16px !important;
        font-style: italic;
        color: #E0E0E0;
        margin: 5px 0 !important;
        line-height: 1.2 !important;
    }

    .developer-tag {
        font-size: 14px !important;
        color: #FFD700; 
        font-weight: bold;
        margin: 0 !important;
    }

    /* மொபைல் போன்களுக்கான Responsive மாற்றம் */
    @media only screen and (max-width: 768px) {
        .logo-img { 
            width: 100px; 
            bottom: -15px; 
            left: 10px;
        }
        .header-banner { 
            padding: 15px 15px 15px 120px;
            min-height: 100px;
        }
        .main-title { font-size: 18px !important; }
        .main-tagline { font-size: 11px !important; }
        .developer-tag { font-size: 10px !important; }
    }

    .stButton > button {
        border-radius: 10px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header (Final Tall Logo Design) ---

import base64
import os

img_name = 'logo.png'
img_path = os.path.join(os.getcwd(), img_name)

# Convert image to base64
def get_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

img_base64 = get_base64(img_path)

# CSS
st.markdown("""
<style>
.header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: -10px;
}

/* 🔥 Tall Logo */
.header img {
    height: 190px;   /* height increase */
    width: auto;     /* ratio maintain */
}

/* Text block */
.text {
    line-height: 1.15;
    margin-top: -8px;
}

/* Title */
.title {
    font-size: 36px;
    font-weight: 900;
    color: #FF4B4B;
    margin: 0;
}

/* Subtitle */
.subtitle {
    font-size: 20px;
    font-weight: 600;
    margin: 2px 0;
    color: #FFFFFF;
}

/* Quote (no highlight) */
.quote {
    font-size: 16px;
    font-style: italic;
    color: #E0E0E0;
    margin-top: 2px;
}

/* Developer */
.dev {
    font-size: 15px;
    color: #FFD700;
    font-weight: bold;
    margin-top: 2px;
}
</style>
""", unsafe_allow_html=True)

# Image HTML
if img_base64:
    img_html = f"<img src='data:image/jpeg;base64,{img_base64}'>"
else:
    img_html = "<div style='font-size:70px;'>🤖</div>"

# Header Layout
st.markdown(f"""
<div class="header">
    {img_html}
    <div class="text">
        <div class="title">AIPSSS</div>
        <div class="subtitle">AI Powered Student Support System</div>
        <div class="quote">"Everyone has the right to education"</div>
        <div class="dev">Developed by Brammadevan</div>
    </div>
</div>
""", unsafe_allow_html=True)
# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic_v3'
)

# --- 🧠 5. AI Logic ---
def ai_response(q, pdf_text=""):
    try:
        # PDF தகவல் இருந்தால் அதைச் சேர்க்கும் பகுதி
        context = f"PDF Context: {pdf_text[:2000]}" if pdf_text else ""
        # மாணவர்களுக்கான வழிகாட்டுதல் மற்றும் சுருக்கமான பாதுகாப்பு எச்சரிக்கை
        system_instruction = (
           "You are 'AIPSSS Mentor', a professional academic and career guide. "
           "Your mission is to assist students in the following areas: "
           "1. SCHOOL & COLLEGE: All subjects (Science, Maths, Social, etc.). "
           "2. LANGUAGES: Tamil and English proficiency. "
           "3. ARTS & DESIGN: Drawing, Painting, Fine Arts, and Graphic Design (CorelDraw, Photoshop). "
            "4. EXAMS: Competitive exams like UPSC, TNPSC, NEET, JEE. "
            "5. SKILLS: Career guidance and skill development. "
    
        "RULES: "
        "- Answer in the SAME LANGUAGE as the user's question (ஆங்கிலத்தில் கேட்டால் ஆங்கிலம், தமிழில் கேட்டால் தமிழ்). "
        "- Be scientifically and factually ACCURATE. Do not hallucinate or create fake stories. "
        "- If a question is about Science/Maths, use clear steps or formulas. "
    
        "STRICT RESTRICTIONS: "
        "- NO Cinema/Entertainment, NO Adult content, NO Illegal topics, NO Mobile Gaming. "
        "- If asked about these, ONLY reply with: 'மன்னிக்கவும், நான் மாணவர்களுக்கான வழிகாட்டி. கல்வி தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்.'"
)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
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
            st.markdown(reply)
            
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
