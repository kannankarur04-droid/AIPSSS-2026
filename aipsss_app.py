import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os

# --- 🔐 1. API Key Setup ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS Voice AI", layout="wide", page_icon="🎓")
st.title("🎓 ஏஐ மாணவர் ஆதரவு அமைப்பு (AIPSSS)")

# --- 🤖 2. சரியான மாடலைக் கண்டுபிடிக்கும் பகுதி ---
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for model_name in available_models:
            if "gemini-1.5-flash" in model_name:
                return model_name
        return available_models[0] if available_models else "gemini-pro"
    except:
        return "gemini-1.5-flash"

# --- 🧠 3. AI பதில் சொல்லும் பகுதி (உங்கள் 'வணக்கம்' ஸ்பெஷல் கோட்) ---
def ai_response(q):
    try:
        working_model_name = get_working_model()
        model = genai.GenerativeModel(working_model_name)
        
        # ஏஐ-க்கு ஒரு உதவியாளராகப் பதில் சொல்லக் கட்டளையிடுகிறோம்
        instruction = """
        You are a friendly AI Student Assistant named AIPSSS. 
        If the user says 'Vanakkam' or 'வணக்கம்', respond with 'வணக்கம் கண்ணன்! நான் உங்களுக்கு இன்று எப்படி உதவ முடியும்?'. 
        For other questions, explain simply in 3 to 5 lines in Tamil language only.
        """
        
        res = model.generate_content(instruction + "\n\nUser Question: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ ஏபிஐ இணைப்பில் சிக்கல்: {str(e)}"

# --- 🔊 4. தமிழ் ஆடியோவாக மாற்றும் பகுதி ---
def speak(text):
    try:
        # முதல் 150 எழுத்துக்களை மட்டும் வேகமாக மாற்றுகிறது
        short_text = text[:150] 
        tts = gTTS(text=short_text, lang='ta') 
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# --- 🚀 5. செயல்பாட்டு பகுதி (Main Logic) ---
st.write("### 🎤 மைக் மூலம் கேள்வி கேட்க அல்லது கீழே டைப் செய்யவும்:")

# மைக் பட்டன்
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN', 
    use_container_width=True,
    key='my_mic'
)

# தட்டச்சு பெட்டி
text_input = st.chat_input("உங்களுடைய கேள்வியை இங்கே கேட்கவும்...")

# மைக் அல்லது டைப்பிங் - எது வந்தாலும் 'prompt' ஆக எடுத்துக்கொள்ளும்
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.markdown(f"**கேள்வி:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt)
            st.info(reply) # நீல நிறப் பெட்டியில் பதில்
            
            # ஆடியோ பதில் உருவாக்கம்
            audio_path = speak(reply)
            if audio_path:
                st.audio(audio_path)
