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

# --- 🎨 2. Styling (CSS) - Modern & Responsive ---
st.set_page_config(page_title="AI Smart Mentor", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* Header Box Design */
    .header-container {
        display: flex;
        align-items: center;
        gap: 30px;
        margin-bottom: 30px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* AI SMART MENTOR Title */
    .main-title { 
        font-family: 'Lexend', sans-serif;
        font-weight: 900; 
        color: #FF4B4B;
        margin: 0 !important; 
        text-transform: uppercase; /* Capital Letters */
        line-height: 1.0 !important;
        white-space: nowrap;
    }

    /* Tagline - White Color */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        color: #FFFFFF !important; /* Pure White */
        margin: 5px 0 0 0 !important;
        font-weight: 500;
        font-style: italic;
    }

    /* Developer - Gold Color */
    .dev-text {
        font-family: 'Lexend', sans-serif;
        color: #FFD700 !important; /* Gold Color */
        margin: 3px 0 0 0 !important;
        font-size: 14px;
        font-weight: 600;
        opacity: 0.9;
    }

    /* Responsive Sizes */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 28px !important; }
        .main-tagline { font-size: 12px !important; }
        .header-container { gap: 15px; padding: 15px; }
        .logo-img { width: 80px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 48px !important; }
        .main-tagline { font-size: 18px !important; }
        .logo-img { width: 140px !important; } /* லோகோ பெரிதாக்கப்பட்டுள்ளது */
    }
    
    /* Input & Button Styling */
    .stButton > button {
        height: 65px !important;
        border-radius: 12px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Display Logic ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        header_html = f'''
            <div class="header-container">
                <img src="data:image/png;base64,{base64_img}" class="logo-img" style="height: auto; object-fit: contain;">
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <p class="main-title">AI SMART MENTOR</p>
                    <p class="main-tagline">"Everyone has the right to education"</p>
                    <p class="dev-text">Developed by Brammadevan</p>
                </div>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
except Exception:
    st.markdown('<h1 style="color:#FF4B4B;">AI SMART MENTOR</h1>', unsafe_allow_html=True)

# --- 🧠 4. AI Core Logic (Accuracy First) ---
def ai_response(q, pdf_text=""):
    try:
        # Strict System Prompt to avoid subject mixing
        sys_prompt = """You are AI Smart Mentor, a professional Educational Assistant developed by Brammadevan. 
        1. Answer strictly based on the subject asked (Auditing, Maths, Psychology, etc.). 
        2. Never mix a student's personal responsibility with professional auditing terms. 
        3. If the question is about personal growth for a 15-year old, focus on ethics and study habits.
        4. Temperature is set to 0.0 for maximum accuracy."""
        
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.0 # துல்லியமான பதில்களுக்கு 0.0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction UI ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic_v3'
)

text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    with st.spinner("கோப்பை வாசிக்கிறேன்..."):
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        for page in doc:
            pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 🚀 6. Output Processing ---
prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages = st.session_state.get('messages', [])
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            
            # Audio Output
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
