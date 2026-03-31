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

# --- 🎨 2. Styling (CSS) - Precision Alignment ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    
    /* Header Container */
    .aipsss-header {
        display: flex;
        align-items: flex-end; 
        justify-content: flex-start;
        gap: 15px; 
        margin-bottom: 30px;
        margin-top: 20px;
        width: 100%;
    }

    /* Logo Size - Large & Clear */
    .main-logo {
        width: 280px; 
        height: auto;
        object-fit: contain;
    }

    /* Content Box - Ultra Tight Spacing */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        text-align: left;
    }

    /* Desktop View */
    @media (min-width: 769px) {
        .main-logo { width: 280px; }
        .main-title { font-size: 5rem !important; line-height: 0.8 !important; }
        .subtitle { font-size: 1.55rem !important; line-height: 1.0 !important; padding-top: 8px; white-space: nowrap; }
        .quote-text { font-size: 1.2rem !important; line-height: 1.0 !important; padding-top: 5px; white-space: nowrap; }
        .developer { font-size: 1.1rem !important; line-height: 1.0 !important; padding-top: 5px; }
    }

    /* Mobile View - Single Line Alignment */
    @media (max-width: 768px) {
        .aipsss-header { gap: 10px; flex-wrap: nowrap; align-items: center; }
        .main-logo { width: 125px !important; }
        .main-title { font-size: 2.8rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.82rem !important; line-height: 1.0 !important; padding-top: 4px; white-space: nowrap; }
        .quote-text { font-size: 0.72rem !important; line-height: 1.0 !important; padding-top: 3px; white-space: nowrap; }
        .developer { font-size: 0.75rem !important; line-height: 1.0 !important; padding-top: 3px; }
    }

    .main-title { font-weight: 900 !important; color: #ff4d4d !important; margin: 0 !important; letter-spacing: -2px; }
    .subtitle { color: #FFD700 !important; margin: 0 !important; font-weight: bold !important; }
    .quote-text { font-style: italic !important; color: #FFD700 !important; margin: 0 !important; }
    .developer { color: #FFFFFF !important; opacity: 0.9 !important; margin: 0 !important; font-weight: 500; }

    /* UI Components */
    .stButton > button { height: 70px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header ---
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
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "gaming", "play", "pubg", "cheat", "hack", "illegal", "movie", "song", "actor", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான உதவிகளை மட்டுமே வழங்க முடியும்."

        system_instruction = "You are AIPSSS, a professional Education Mentor. Answer based on provided PDF or general knowledge. Strictly no gaming/entertainment."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# PDF பதிவேற்றம் - நீங்கள் மாற்றிய வாசகம்
uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])

pdf_extracted_text = ""
if uploaded_pdf:
    with st.spinner("PDF கோப்பைப் படிக்கிறேன்..."):
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ '{uploaded_pdf.name}' கோப்பு இணைக்கப்பட்டது!")

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_bramma')
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("தேடுகிறேன்..."):
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
