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

# --- 🎨 2. Styling (CSS) - Responsive Design ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    
    /* AIPSSS Header Container */
    .aipsss-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        padding: 20px;
        flex-wrap: wrap;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    /* Logo Size */
    .main-logo {
        width: 200px;
        height: auto;
        transition: 0.3s;
    }

    .content-box {
        text-align: left;
    }

    .main-title {
        font-size: 4.5rem !important;
        color: #ff4d4d !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.9 !important;
    }

    .subtitle {
        font-size: 1.5rem !important;
        color: #FFD700 !important; /* Gold */
        margin: 5px 0 !important;
        font-weight: bold !important;
    }

    .tagline {
        font-style: italic !important;
        color: #FFD700 !important; /* Gold */
        margin-top: 8px !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }

    .developer {
        font-size: 0.9rem !important;
        color: #FFFFFF !important; /* White */
        opacity: 0.8 !important;
        margin-top: 5px !important;
    }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .aipsss-header { flex-direction: column; text-align: center; gap: 15px; }
        .content-box { text-align: center; }
        .main-logo { width: 120px; }
        .main-title { font-size: 3rem !important; }
        .subtitle { font-size: 1.1rem !important; }
    }

    /* UI Components */
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
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
            <div class="logo-box">
                <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            </div>
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B; text-align:center;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        # Guardrails
        restricted = ["cinema", "movie", "actor", "song", "adult", "porn", "violence", "illegal", "hack", "சினிமா", "படம்", "நடிகர்", "ஆபாசம்"]
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும், AIPSSS ஒரு கல்வி மற்றும் வேலைவாய்ப்பு சார்ந்த தளம் மட்டுமே. தேவையற்ற தகவல்களை என்னால் வழங்க முடியாது."

        system_instruction = "You are AIPSSS, a dedicated Educational Mentor. Only help with studies and career."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_mic_final')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேட", type=["pdf"])

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
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            
            # Audio response logic
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except Exception:
                pass
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
