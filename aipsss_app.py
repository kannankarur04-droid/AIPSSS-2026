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

# --- 🎨 2. Styling (CSS) - Ultra Precise Alignment ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* Header Container: Logo Left, Text Side-by-Side */
    .aipsss-header {
        display: flex;
        align-items: flex-end; /* Text sits at the bottom of the logo */
        justify-content: flex-start;
        gap: 15px;
        margin-bottom: 35px;
        margin-top: 20px;
    }

    /* Logo Size - Large as requested */
    .main-logo {
        width: 260px; 
        height: auto;
        object-fit: contain;
    }

    /* Content Box: Stacked lines on the left */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        text-align: left;
    }

    .main-title {
        font-size: 4.8rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important;
    }

    .subtitle {
        font-size: 1.6rem !important;
        color: #FFD700 !important; /* Gold */
        margin: 0 !important;
        font-weight: bold !important;
        line-height: 1.0 !important;
        padding-top: 8px;
    }

    .quote-text {
        font-style: italic !important;
        color: #FFD700 !important; /* Gold */
        margin: 0 !important;
        line-height: 1.0 !important;
        padding-top: 4px;
        font-size: 1.15rem !important;
    }

    .developer {
        font-size: 1rem !important;
        color: #FFFFFF !important; /* White */
        opacity: 0.8 !important;
        margin: 0 !important;
        line-height: 1.0 !important;
        padding-top: 5px;
    }

    /* Mobile View: Center everything */
    @media (max-width: 768px) {
        .aipsss-header { flex-direction: column; align-items: center; text-align: center; }
        .content-box { text-align: center; }
        .main-logo { width: 180px; }
        .main-title { font-size: 3.2rem !important; }
    }

    /* UI Styles */
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine (Strict Educational Focus) ---
def ai_response(user_query, pdf_text=""):
    try:
        # 🚫 Gaming, Illegal & Harmful Keywords Block
        restricted = [
            "game", "pubg", "free fire", "cheat", "hack", "illegal", "kill", "drug", "adult", "porn", "suicide",
            "சினிமா", "விளையாட்டு", "கொலை", "பாடல்", "நடிகர்", "சண்டை", "திருட்டு"
        ]
        
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும் கண்ணன், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான உதவிகளை மட்டுமே வழங்க முடியும். கேமிங் அல்லது தேவையற்ற தகவல்களை என்னால் வழங்க முடியாது."

        # System Instruction for AI behavior
        system_instruction = """
        You are AIPSSS, a professional Education and Career Mentor. 
        - ONLY answer queries related to: Education, Competitive Exams, Career Guidance, Job Opportunities, and Skills.
        - STRICTLY decline Gaming, Movies, Illegal acts, or general entertainment.
        - If someone asks something non-educational, say: 'மன்னிக்கவும், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான வழிகாட்டி மட்டுமே.'
        - Talk naturally, avoid being like a monk or robot.
        """

        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.3)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. Chat Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='mic_aipsss_final_v12')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF கோப்புகள்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF இணைக்கப்பட்டது!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
