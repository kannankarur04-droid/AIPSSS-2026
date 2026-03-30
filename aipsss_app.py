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

# --- 🎨 2. Styling (CSS) - Mobile & Logo Friendly ---
st.set_page_config(page_title="AIPSSS", layout="centered")

st.markdown("""
    <style>
    /* தேவையற்ற இடைவெளிகளைக் குறைக்க */
    .block-container { padding-top: 1rem; }
    
    /* தலைப்பு (லோகோ இல்லையென்றால்) */
    .fallback-title { font-size: 45px; font-weight: 900; text-align: center; color: #FF4B4B; margin-top: -50px; letter-spacing: 3px; }

    /* மைக் பட்டன் - பெரிய அளவு */
    .stButton > button { height: 85px !important; width: 100% !important; border-radius: 15px !important; font-size: 22px !important; font-weight: bold; background-color: #FF4B4B !important; color: white !important; }
    
    /* படங்களைச் சுற்றி பெட்டியை (Border) நீக்க */
    div[data-testid="stImage"] img {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    
    /* PDF அப்லோடர் */
    .stFileUploader { margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Logo Placement ---
logo_path = os.path.join(os.path.dirname(__file__), 'aipsss_logo.png')
if os.path.exists(logo_path):
    # லோகோவை நடுவில் வைக்க
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(Image.open(logo_path), use_container_width=True)
else:
    st.markdown('<p class="fallback-title">AIPSSS</p>', unsafe_allow_html=True)

# --- 🧠 4. AI Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AIPSSS, a kind Education Assistant. Answer educational doubts briefly (max 4 lines). Encourage the student."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction - Voice (First) ---
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_final_mic')

# --- ⌨️ 6. Interaction - Input & PDF (Bottom) ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# PDF அப்லோடர்
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 🚀 7. Generate Response ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # Audio Output
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
