import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (Vertical Alignment Fix) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* லோகோ மற்றும் பெயரைச் சீராக அடுக்க */
    [data-testid="stHorizontalBlock"] {
        align-items: center; 
        display: flex;
        gap: 15px;
        margin-top: -20px;
    }

    .main-title { 
        font-size: 52px !important; 
        font-weight: 900; 
        color: #FF4B4B !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }
    
    .main-tagline {
        font-size: 18px !important; 
        text-align: center; 
        color: #FFD700 !important;
        margin-top: 5px;
        font-weight: bold;
    }
    
    /* மைக் பட்டன் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
    }

    /* PDF Uploader */
    .stFileUploader { margin-top: -15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Fix (Checking for Robot Image) ---
# கவனிக்கவும்: படத்தின் பெயர் GitHub-ல் 'aipsss_robot.png' என்று இருக்க வேண்டும்
img_name = 'aipsss_robot.png' 
# கோடில் படத்தைத் தேடும் பாதை
img_path = os.path.join(os.getcwd(), img_name)

col1, col2 = st.columns([1, 4])

# படம் இருக்கிறதா என்று சோதித்து காட்டவும்
try:
    if os.path.exists(img_path):
        with col1:
            st.image(Image.open(img_path), width=85)
        with col2:
            st.markdown('<p class="main-title">AIPSSS</p>', unsafe_allow_html=True)
    else:
        # படம் இல்லையென்றால்Fall Back
        st.markdown(f'<p class="main-title" style="text-align:center;">AIPSSS</p>', unsafe_allow_html=True)
        # படக் கோப்பு ஏன் வரவில்லை என்ற குறிப்பு அட்மினுக்கு மட்டும்
        # st.warning(f"Note: {img_name} not found in root.")

except FileNotFoundError:
     st.markdown(f'<p class="main-title" style="text-align:center;">AIPSSS</p>', unsafe_allow_html=True)

st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)

# --- 🧠 4. AI Logic (Accuracy Guaranteed) ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": "You are AIPSSS, a highly accurate Education Assistant. Double-check facts and Tamil numbers (90 is தொண்ணூறு). Encourage the student."
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction ---
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='v_mic')

# --- 🚀 6. Process Input ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc: pdf_context += page.get_text()
    st.success("✅ PDF தயார்!")

# --- 💬 7. Display Output ---
prompt = voice_input if voice_input else text_input
if prompt:
    with st.chat_message("user"): st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("r.mp3")
            st.audio("r.mp3", autoplay=True)
