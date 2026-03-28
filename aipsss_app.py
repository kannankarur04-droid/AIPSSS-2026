import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# --- 🔐 API Key Setup (பாதுகாப்பிற்காக st.secrets-ல் இருந்து) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

# --- 🎨 ஆப்பின் வடிவமைப்பு (UI Setup with Logo & Favicon) ---
st.set_page_config(
    page_title="AIPSSS: Voice & Tamil", 
    layout="wide", 
    page_icon="🎓" # பிரவுசர் டேபில் லோகோ
)

# --- 💅 திரையில் அழகிய வண்ணம் (CSS Styling) ---
st.markdown("""
<style>
    /* தலைப்பு மற்றும் பின்னணி நிறம் */
    .stApp {
        background-color: #f0f8ff; /* லேசான நீல நிறம் */
    }
    
    /* ஏஐ-ஆல் இயங்கும் மாணவர் ஆதரவு அமைப்பு (AIPSSS) தலைப்பு */
    .main-title {
        color: #0047AB; /* அடர் நீல நிறம் */
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    
    /* லோகோ மற்றும் தலைப்பு இணைந்த பகுதி */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
    }
    
    .logo-icon {
        font-size: 3rem; /* லோகோவின் அளவு */
        margin-right: 15px;
    }
    
    /* பதில் வரும் பகுதி */
    .assistant-message {
        background-color: #E6F3FF; /* பதிலுக்கான பின்னணி நிறம் */
        border-left: 5px solid #007FFF; /* நீல நிற பார்டர் */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* "Think..." சுழற்சி நிறம் */
    .stSpinner > div > div {
        border-color: #007FFF transparent #007FFF transparent !important;
    }
    
    /* ஆடியோ பிளேயர் நிறம் */
    audio {
        width: 100%;
        background-color: #E6F3FF;
    }
</style>
""", unsafe_allow_html=True)

# --- 🖼️ லோகோ மற்றும் தலைப்பு (Logo & Main Title with Tamil Script) ---
st.markdown("""
<div class="logo-container">
    <div class="logo-icon">🎓</div>
    <div class="main-title">ஏஐ-ஆல் இயங்கும் மாணவர் ஆதரவு அமைப்பு (AIPSSS)</div>
</div>
""", unsafe_allow_html=True)

# --- 🤖 ஏஐ பதில் சொல்லும் பகுதி ---
def get_ai_response(q):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # தமிழிலேயே பதில் சொல்லக் கட்டளையிடுகிறோம்
        system_instruction = "You are a helpful educational assistant. Explain concepts simply and clearly in Tamil. Give a short 3-line answer."
        res = model.generate_content(system_instruction + "\n\nQuestion: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ ஏபிஐ இணைப்பில் சிக்கல். மீண்டும் முயற்சிக்கவும்."

# --- 🔊 தமிழில் வாசிக்கும் ஆடியோ பதில் ---
def speak(text):
    try:
        # முதல் 150 எழுத்துக்களை மட்டும் வேகமாக மாற்றுகிறது
        short_text = text[:150] 
        tts = gTTS(text=short_text, lang='ta')
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# --- 🚀 Main Logic ---
prompt = st.chat_input("உங்களுடைய கேள்வியை இங்கே டைப் செய்யவும்...")

if prompt:
    # மாணவர் கேள்வி
    with st.chat_message("user"):
        st.markdown(f"**உங்கள் கேள்வி:** {prompt}")

    # ஏஐ பதில்
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = get_ai_response(prompt)
            # பதிலுக்கு அழகிய வண்ணம் (CSS)
            st.markdown(f'<div class="assistant-message">{reply}</div>', unsafe_allow_html=True)
            
            # ஆடியோ பதில்
            audio_file = speak(reply)
            if audio_file:
                st.audio(audio_file)
