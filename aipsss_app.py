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

# --- 🎨 2. Styling (CSS) - White Theme based on "My Idea" ---
st.set_page_config(page_title="AIPSSS - Student Support", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* White Background */
    .stApp { background-color: #FFFFFF; }
    
    .block-container { padding-top: 2rem !important; max-width: 1200px; }
    
    /* Header Layout */
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 20px; 
        margin-bottom: 30px;
        padding: 10px;
    }

    /* Logo size */
    .main-logo {
        width: 120px !important; 
        height: auto;
    }

    /* Content Box with strict line spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        text-align: left;
    }

    /* Red Title AIPSSS */
    .main-title { 
        font-size: 3rem !important;
        font-weight: 800; 
        color: #FF0000 !important; /* Pure Red */
        margin: 0 !important; 
        padding: 0 !important;
        line-height: 0.9 !important;
    }

    /* Yellow Background for Subtitles */
    .subtitle-container {
        background-color: #FFFF00; /* Bright Yellow */
        padding: 5px;
        margin-top: 5px;
        display: inline-block;
    }

    .subtitle-text {
        font-size: 1.2rem !important;
        color: #000000 !important; 
        margin: 0 !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
    }

    /* UI Elements visibility */
    .stMarkdown, p, label { color: #000000 !important; }
    .stButton > button { background-color: #F0F2F6 !important; color: black !important; border: 1px solid #CCC !important; }
    
    /* Chat bubbles for white theme */
    [data-testid="stChatMessage"] {
        background-color: #F8F9FA !important;
        border: 1px solid #EEE !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Implementation ---
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
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <div class="subtitle-container">
                    <p class="subtitle-text">AI Powered Student Support System</p>
                    <p class="subtitle-text">"Everyone has the right to education"</p>
                </div>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "play", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி தொடர்பான உதவியாளர் மட்டுமே."

        system_instruction = "You are AIPSSS, an AI Powered Student Support System. Provide helpful and academic guidance."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI ---

# PDF Section
st.write("📂 **PDF மூலம் தேடுவதற்கு**")
uploaded_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
pdf_extracted_text = ""

if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ {uploaded_pdf.name} Loaded")

# Mic Button
voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final')

# Chat Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Interaction
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")
prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
