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

# --- 🎨 2. Styling (CSS) - Professional & Tight Layout ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* 1. ஹெட்டர் பெட்டி - Rectangle Box Size குறைக்கப்பட்டுள்ளது */
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 35px; 
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.05); 
        padding: 15px 40px; /* உயரத்தைக் குறைக்க 15px padding */
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 2. லோகோ - பெரிதாக்கப்பட்டுள்ளது (Big Logo) */
    .main-logo {
        width: 180px !important; 
        height: auto;
        object-fit: contain;
        flex-shrink: 0;
    }

    /* 3. எழுத்துக்கள் பெட்டி அலைன்மென்ட் */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
        padding-bottom: 5px; 
    }

    /* 4. AI STUDENT MENTOR - சிகப்பு நிறம் & நெருக்கமான இடைவெளி */
    .main-title { 
        font-weight: 950; 
        color: #FF4B4B !important; /* சிகப்பு நிறம் */
        text-transform: uppercase;
        margin: 0 !important; 
        line-height: 0.8 !important; 
        letter-spacing: -2px;
        font-size: 52px !important;
    }

    /* 5. பொன்மொழி - வெள்ளை நிறம் & மேலே நகர்த்தப்பட்டுள்ளது */
    .subtitle {
        font-size: 1.15rem !important;
        color: #FFFFFF !important; /* வெள்ளை நிறம் */
        margin: 0 !important;
        padding-top: 2px !important; 
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* 6. டெவலப்பர் - தங்க நிறம் & மேலே நகர்த்தப்பட்டுள்ளது */
    .developer {
        font-size: 1.05rem !important;
        color: #FFD700 !important; /* தங்க நிறம் */
        margin: 0 !important;
        padding-top: 3px !important; 
        font-weight: bold;
        line-height: 1.0 !important;
        opacity: 0.9;
    }

    /* மொபைல் சீரமைப்பு */
    @media (max-width: 768px) {
        .aipsss-header { gap: 15px; padding: 10px 15px; }
        .main-logo { width: 90px !important; }
        .main-title { font-size: 1.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ ஹெட்டர் டிஸ்ப்ளே (HTML) ---
if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI STUDENT MENTOR</h1>
                <p class="subtitle">Everyone has the right to education</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Assets ---
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
                <h1 class="main-title">AI STUDENT MENTOR</h1>
                <p class="subtitle">Everyone has the right to education</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        forbidden = ["game", "gaming", "play", "pubg", "cheat", "hack", "illegal", "movie", "song", "விளையாட்டு", "சினிமா"]
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான வழிகாட்டி மட்டுமே. பொழுதுபோக்கு தொடர்பான தகவல்களை வழங்க முடியாது."

        system_instruction = "You are AI Student Mentor, a professional Education Mentor. Answer precisely. Strictly no gaming/entertainment stuff."
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

uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேடுவதற்கு", type=["pdf"])
pdf_extracted_text = ""

if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_extracted_text = "".join([page.get_text() for page in doc])
    st.success(f"✅ '{uploaded_pdf.name}' Loaded!")

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_v40')
text_input = st.chat_input("கேள்வியைக் கேட்கவும்...")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            reply = ai_response(prompt, pdf_extracted_text)
            st.markdown(reply)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except: pass
    st.session_state.messages.append({"role": "assistant", "content": reply})
