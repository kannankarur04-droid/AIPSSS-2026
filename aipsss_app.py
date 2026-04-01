import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF
import base64

# --- 1. பக்க வடிவமைப்பு (Page Config) ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

# --- 2. 🔐 API Key Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY! Please check your Streamlit secrets.")
    st.stop()

# --- 3. 🎨 CSS Styling (படத்தில் உள்ளவாறு அலைன்மென்ட் செய்ய) ---
st.markdown("""
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
    /* பின்னணி நிறம் */
    .stApp { background-color: #0e1117; }
    
    /* ஹெட்டர் கண்டெய்னர் - லோகோவும் எழுத்தும் பக்கவாட்டில் வர */
    .mentor-header {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 20px;
        padding: 10px 0;
        margin-bottom: 15px;
    }

    /* லோகோ அளவு */
    .header-logo {
        width: 110px !important;
        height: auto;
    }

    /* எழுத்துக்களின் பெட்டி */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* AI STUDENT MENTOR - சிகப்பு நிறம் */
    .header-text h1 {
        font-family: 'Lexend', sans-serif;
        font-size: 42px !important;
        color: #FF4B4B !important;
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 1.0 !important;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    /* Tagline - வெள்ளை நிறம் */
    .tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 18px !important;
        color: #FFFFFF !important;
        margin: 5px 0 2px 0 !important;
        font-style: italic;
    }

    /* Developer - தங்க நிறம் */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 14px !important;
        color: #FFD700 !important;
        margin: 0 !important;
        font-weight: bold;
    }

    /* Chat Input மற்றும் இதர வடிவமைப்பு */
    .stChatInputContainer { border-radius: 15px !important; }
    .stFileUploader { margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 🧠 Session State for Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. 🖼️ Header Logic (Image to Base64) ---
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')
base64_img = get_base64_image(img_path)

# ஹெட்டரைத் திரையில் காட்டுதல்
if base64_img:
    st.markdown(f'''
        <div class="mentor-header">
            <img src="data:image/png;base64,{base64_img}" class="header-logo">
            <div class="header-text">
                <h1>AI STUDENT MENTOR</h1>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B;">AI STUDENT MENTOR</h1>', unsafe_allow_html=True)

# --- 6. 🤖 AI Engine Function ---
def ai_response(user_query, pdf_text=""):
    try:
        system_instruction = "You are AI Student Mentor. Answer precisely in the language of the user."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-3:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 7. 📥 PDF Handling ---
uploaded_pdf = st.file_uploader("📂 PDF கோப்புகளை இங்கே பதிவேற்றவும்", type=["pdf"])
pdf_extracted_text = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success("PDF வெற்றிகரமாகப் படிக்கப்பட்டது!")

# --- 8. 💬 Chat Display & Input ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# மைக் மற்றும் டெக்ஸ்ட் இன்புட்
col1, col2 = st.columns([0.1, 0.9])
with col1:
    voice_input = speech_to_text(start_prompt="🎤", language='ta-IN', key='mic_v1')

text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")
prompt = voice_input if voice_input else text_input

if prompt:
    # யூசர் மெசேஜ்
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI மெசேஜ்
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            
            # ஆடியோ பதில் (TTS)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
                
    st.session_state.messages.append({"role": "assistant", "content": reply})
