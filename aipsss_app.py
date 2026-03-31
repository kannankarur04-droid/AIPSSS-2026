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

# --- 🎨 2. Styling (CSS) - Ultra Tight Alignment ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* AIPSSS Header Container */
    .aipsss-header { 
        display: flex; 
        align-items: flex-end; /* பாதம் அருகில் அலைன் செய்ய */
        justify-content: center; 
        gap: 2px; /* மிகக் குறைந்த இடைவெளி - பெயர்கள் லோகோவை ஒட்டி வரும் */
        padding: 10px; 
        flex-wrap: nowrap; /* மொபைலில் உடையாமல் இருக்க */
        margin-top: 20px; 
        margin-bottom: 30px; 
    }

    /* Logo Size */
    .main-logo { width: 210px; height: auto; transition: 0.3s; }

    .content-box { text-align: left; margin-left: 0px; }

    /* Title & Typography */
    .main-title { 
        font-size: 4.5rem !important; 
        color: #ff4d4d !important; 
        margin: 0 !important; 
        font-weight: 900 !important; 
        line-height: 0.8 !important; 
        letter-spacing: -2px;
    }
    .subtitle { 
        font-size: 1.5rem !important; 
        color: #FFD700 !important; 
        margin: 0 !important; 
        font-weight: bold !important; 
        line-height: 1.0 !important;
        padding-top: 5px;
    }
    .tagline { 
        font-style: italic !important; 
        color: #FFD700 !important; 
        margin: 0 !important; 
        line-height: 1.0 !important;
        padding-top: 3px;
        font-size: 1.1rem !important;
    }
    .developer { 
        font-size: 0.9rem !important; 
        color: #FFFFFF !important; 
        opacity: 0.8 !important; 
        margin: 0 !important; 
        line-height: 1.0 !important;
        padding-top: 3px;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .aipsss-header { gap: 5px; }
        .main-logo { width: 130px; }
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
            <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        restricted = ["cinema", "movie", "actor", "adult", "violence", "kill", "fight", "சினிமா", "படம்", "நடிகர்", "ஆபாசம்"]
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும், நான் ஒரு கல்வி வழிகாட்டி. இது போன்ற கேள்விகளுக்கு என்னால் பதில் சொல்ல முடியாது. உங்கள் படிப்பு தொடர்பாக ஏதேனும் உதவி தேவையா?"

        system_instruction = "You are AIPSSS, a professional Education Assistant. Be natural and direct. Only education topics."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.3)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='mic_final_v5_tight')
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
        with st.spinner("சிந்திக்கிறேன்..."):
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
