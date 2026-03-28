import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os

# --- 🔐 API Key Setup ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

# --- 🎨 ஆப் வடிவமைப்பு (UI Setup) ---
st.set_page_config(page_title="AIPSSS Voice AI", layout="wide", page_icon="🎓")

# CSS மூலம் வண்ணங்கள் மற்றும் லோகோவை அழகுபடுத்துதல்
st.markdown("""
    <style>
    .main-title {
        color: #0047AB;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #0047AB;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 ஏஐ மாணவர் ஆதரவு அமைப்பு (AIPSSS)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">குரல் மூலம் தேடுங்கள் அல்லது தட்டச்சு செய்யுங்கள்</div>', unsafe_allow_html=True)

# 💾 மெமரி (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# பழைய மெசேஜ்களைத் திரையில் காட்டுதல்
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 🎤 குரல் தேடல் பகுதி (Speech to Text) ---
st.write("### 🎤 குரல் மூலம் கேள்வி கேட்க:")
text_from_voice = speech_to_text(
    start_prompt="பேசத் தொடங்க இங்கே கிளிக் செய்யவும்",
    stop_prompt="நிறுத்த இங்கே கிளிக் செய்யவும்",
    language='ta-IN', # தமிழ் மொழியைப் புரிந்து கொள்ள
    use_container_width=True,
    key='speech'
)

# ⌨️ தட்டச்சு செய்ய (Chat Input)
text_input = st.chat_input("உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யவும்...")

# கேள்வியைத் தீர்மானித்தல் (குரல் அல்லது தட்டச்சு)
prompt = text_from_voice if text_from_voice else text_input

# --- 🤖 ஏஐ பதில் மற்றும் ஆடியோ பங்க்ஷன்கள் ---
def get_ai_response(q):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # ஏஐ-க்கு ஒரு உதவியாளராகப் பதில் சொல்லக் கட்டளையிடுகிறோம்
        instruction = "You are a helpful student assistant. If user greets, greet back in Tamil. Explain concepts simply in 3-5 lines in Tamil language only."
        res = model.generate_content(instruction + "\n\nUser Question: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ ஏபிஐ இணைப்பில் சிக்கல்: {str(e)}"

def speak(text):
    try:
        # முதல் 150 எழுத்துக்களை மட்டும் வேகமாக மாற்றுகிறது
        short_text = text[:150] 
        tts = gTTS(text=short_text, lang='ta')
        tts.save("response.mp3")
        return "response.mp3"
    except:
        return None

# --- 🚀 செயல்படும் பகுதி (Main Logic) ---
if prompt:
    # மாணவர் கேள்வி
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ஏஐ பதில்
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = get_ai_response(prompt)
            st.info(reply) # நீல நிறப் பெட்டியில் பதில்
            
            # ஆடியோ பிளேயர்
            audio_path = speak(reply)
            if audio_path:
                st.audio(audio_path)

    st.session_state.messages.append({"role": "assistant", "content": reply})
