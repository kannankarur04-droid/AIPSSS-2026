import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF

# --- 🔐 1. API Key Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in Secrets!")
    st.stop()

# --- 🎨 2. UI & Big Mic Styling (CSS) ---
st.set_page_config(page_title="AIPSSS - Life Time Assistant", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    /* பெரிய மைக் பட்டன் வடிவமைப்பு */
    .stButton > button {
        height: 80px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: #FF4B4B !important;
        color: white !important;
        border: 2px solid #FF4B4B !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF7676 !important;
        border-color: #FF7676 !important;
        transform: scale(1.02);
    }
    /* சாட் பாக்ஸ் ஸ்டைல் */
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 AIPSSS - Student Support System")
st.markdown("### *அனைத்து மாணவர்களுக்கான பிரத்யேக கல்வி உதவியாளர்*")
st.write("---")

# --- 🧠 3. AI Core Logic (The Brain) ---
def ai_response(q, pdf_text=""):
    try:
        # PDF தகவல் இருந்தால் அதைச் சேர்த்துக் கொள்கிறோம்
        context = f"பயனர் பகிர்ந்துள்ள PDF தகவல்: {pdf_text[:2000]}" if pdf_text else ""
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """
                    You are a 'LIFE TIME EDUCATION ASSISTANT'. 
                    - SCOPE: Answer School, College, Competitive exams (JEE, NEET, TNPSC), and Career queries.
                    - TONE: Encouraging, professional, and friendly. 
                    - RULES:
                      1. Respond ONLY to educational queries. 
                      2. If asked about movies, politics, or celebrities, say: 'மன்னிக்கவும், நான் ஒரு கல்வி உதவியாளர். கல்வி சார்ந்த கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்.'
                      3. Respond in English for English/Tanglish, and Tamil for Tamil.
                      4. Keep answers brief (max 5 lines).
                    """
                },
                {"role": "user", "content": f"{context}\n\nUser Question: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- 📁 4. PDF Text Extraction ---
def get_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- 🎙️ 5. Audio Processing ---
def speak(text):
    try:
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', text))
        lang = 'ta' if is_tamil else 'en'
        tts = gTTS(text=text[:300], lang=lang)
        tts.save("reply.mp3")
        return "reply.mp3"
    except:
        return None

# --- 🚀 6. Main Interaction ---
st.sidebar.header("📁 Study Materials")
uploaded_pdf = st.sidebar.file_uploader("உங்கள் பாடப் புத்தகத்தை (PDF) பதிவேற்றவும்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    pdf_context = get_pdf_text(uploaded_pdf)
    st.sidebar.success("PDF தயார்! இப்போது கேள்வி கேட்கலாம்.")

# மைக் பட்டன் - பெரிய அளவில்
voice_data = speech_to_text(
    start_prompt="🎤 CLICK TO ASK (பேச இங்கே அழுத்தவும்)",
    stop_prompt="🛑 STOP (நிறுத்த அழுத்தவும்)",
    language='ta-IN',
    use_container_width=True,
    key='big_mic'
)

text_data = st.chat_input("உங்கள் கல்வி சந்தேகத்தை இங்கே எழுதவும்...")

prompt = voice_data if voice_data else text_data

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # ஆடியோ பதில்
            audio_file = speak(reply)
            if audio_file:
                st.audio(audio_file, autoplay=True)
