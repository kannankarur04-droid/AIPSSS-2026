import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os

# 🔐 1. API Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS Voice", layout="wide", page_icon="🎓")
st.title("🎓 AI Student Support (Voice Enabled)")

# 🤖 2. சரியான மாடலைக் கண்டுபிடிக்கும் பகுதி
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for model_name in available_models:
            if "gemini-1.5-flash" in model_name:
                return model_name
        return available_models[0] if available_models else "gemini-pro"
    except:
        return "gemini-1.5-flash"

# 🧠 3. AI பதில் சொல்லும் பகுதி
def ai_response(q):
    try:
        working_model_name = get_working_model()
        model = genai.GenerativeModel(working_model_name)
        # எளிய தமிழில் பதில் சொல்லக் கட்டளை
        res = model.generate_content("Explain simply in Tamil: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🔊 4. ஆடியோவாக மாற்றும் பகுதி
def speak(text):
    try:
        short_text = text[:150] 
        tts = gTTS(text=short_text, lang='ta') # தமிழில் பேச 'ta'
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# 🚀 5. Main Logic (குரல் மற்றும் தட்டச்சு)
st.write("### 🎤 மைக் மூலம் கேள்வி கேட்க அல்லது கீழே டைப் செய்யவும்:")

voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN', 
    use_container_width=True,
    key='my_mic'
)

text_input = st.chat_input("Ask your question here...")

# மைக் அல்லது டைப்பிங் - எது வந்தாலும் 'prompt' ஆக எடுத்துக்கொள்ளும்
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ai_response(prompt)
            st.markdown(reply)
            
            audio_file = speak(reply)
            if audio_file:
                st.audio(audio_file)
