import streamlit as st
import google.generativeai as genai
import time
import re
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# 🔐 API Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS Voice", layout="wide", page_icon="🎓")
st.title("🎓 AI Student Support (Voice Enabled)")

# 🤖 சரியான மாடலைக் கண்டுபிடிக்கும் பகுதி
def get_working_model():
    # உங்கள் ஏபிஐ கீ-க்கு எந்தெந்த மாடல்கள் வேலை செய்யும் என்று பட்டியலிடும்
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 1.5 flash இருந்தால் அதை எடு, இல்லையென்றால் முதல் மாடலை எடு
    for model_name in available_models:
        if "gemini-1.5-flash" in model_name:
            return model_name
    return available_models[0] if available_models else "gemini-pro"

# 🧠 AI பதில் சொல்லும் பகுதி
def ai_response(q):
    try:
        working_model_name = get_working_model()
        model = genai.GenerativeModel(working_model_name)
        res = model.generate_content("Explain simply: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🔊 ஆடியோவாக மாற்றும் பகுதி (இது 38-வது வரியில் தொடங்கும்)
def speak(text):
    try:
        short_text = text[:150]
        tts = gTTS(text=short_text, lang='en')
        tts.save("output.mp3")
        return "output.mp3"
    except Exception as e: # 👈 இந்த வரி இங்கே கண்டிப்பாக இருக்க வேண்டும்!
        return None

voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='en-IN', 
    use_container_width=True,
    key='my_mic'
)

# ⌨️ தட்டச்சு பெட்டி (இது இப்போது சரியாக வேலை செய்யும்)
text_input = st.chat_input("Ask your question here...")

# மைக் அல்லது டைப்பிங்
prompt = voice_input if voice_input else text_input
)
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# 🚀 Main Logic
prompt = st.chat_input("Ask your question here...")

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
