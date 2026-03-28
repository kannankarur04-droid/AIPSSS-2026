import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os

# --- 🔐 1. API Key Setup (பாதுகாப்பிற்காக st.secrets-ல் இருந்து) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

# --- 🎨 2. ஆப்பின் வடிவமைப்பு (UI & Styling) ---
st.set_page_config(page_title="AIPSSS Expert", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .main-title {
        color: #0047AB;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #555;
        text-align: center;
        margin-bottom: 25px;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 ஏஐ மாணவர் ஆதரவு அமைப்பு (AIPSSS)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">குரல் மூலம் தேடுங்கள் அல்லது தட்டச்சு செய்யுங்கள்</div>', unsafe_allow_html=True)

# 💾 மெமரி (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# பழைய உரையாடல்களைக் காட்டுதல்
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 🎤 3. குரல் தேடல் (Voice Search) ---
st.write("### 🎤 குரல் மூலம் கேள்வி கேட்க:")
text_from_voice = speech_to_text(
    start_prompt="பேசத் தொடங்க இங்கே கிளிக் செய்யவும்",
    stop_prompt="நிறுத்த இங்கே கிளிக் செய்யவும்",
    language='ta-IN', 
    use_container_width=True,
    key='speech'
)

# ⌨️ தட்டச்சு செய்ய (Chat Input)
text_input = st.chat_input("உங்களுடைய கேள்வியை இங்கே கேட்கவும்...")

# கேள்வியைத் தீர்மானித்தல்
prompt = text_from_voice if text_from_voice else text_input

# --- 🤖 4. ஏஐ பதில் (404 Error வராமல் தடுக்கும் முறை) ---
def get_ai_response(q):
    # முதலில் 'gemini-1.5-flash' முயற்சிக்கும், இல்லையென்றால் 'gemini-pro' முயற்சிக்கும்
    models_to_try = ["gemini-1.5-flash", "gemini-pro"]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            # ஏஐ-க்கு ஒரு ஆசிரியராகப் பதில் சொல்லக் கட்டளையிடுகிறோம்
            instruction = "You are a helpful teacher. If user says Vanakkam, reply with Vanakkam. Explain concepts briefly in 3-5 lines in Tamil language only."
            res = model.generate_content(instruction + "\n\nQuestion: " + q)
            return res.text
        except Exception:
            continue
            
    return "⚠️ ஏபிஐ இணைப்பில் சிக்கல். சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."

# --- 🔊 5. தமிழ் ஆடியோ பதில் (Voice Output) ---
def speak(text):
    try:
        # முதல் 150 எழுத்துக்களை மட்டும் வேகமாக மாற்றுகிறது
        short_text = text[:150] 
        tts = gTTS(text=short_text, lang='ta')
        tts.save("response.mp3")
        return "response.mp3"
    except:
        return None

# --- 🚀 6. செயல்பாட்டு பகுதி (Main Execution) ---
if prompt:
    # மாணவர் கேள்வி
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**கேள்வி:** {prompt}")

    # ஏஐ பதில்
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = get_ai_response(prompt)
            st.info(reply)
