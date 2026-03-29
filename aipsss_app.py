import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re

# --- 🔐 1. Groq API Key Setup ---
# Streamlit Secrets-ல் GROQ_API_KEY இருப்பதை உறுதி செய்யவும்
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY! Please check Streamlit Secrets.")
    st.stop()

# --- 🎨 2. UI Configuration ---
st.set_page_config(page_title="AI Student Support", layout="wide", page_icon="🎓")
st.title("🎓 AI Powered Student Support System")
st.markdown("### *Your Intelligent Bilingual Learning Assistant*")
st.write("---")

# --- 🧠 3. AI Core Logic (Updated Model Name) ---
def ai_response(q):
    try:
        # ⚠️ இங்கே புதிய மாடல் பெயர் சரியாக கொடுக்கப்பட்டுள்ளது
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """
                    You are a professional bilingual student assistant. 
                    - If user asks in Tamil, respond in simple Tamil. 
                    - If user asks in English, respond in simple English. 
                    - If user says 'Vanakkam' or 'வணக்கம்', reply 'வணக்கம் கண்ணன்! நான் உங்களுக்கு இன்று எப்படி உதவ முடியும்?'.
                    - Keep explanations brief, clear, and educational (3-5 lines).
                    """
                },
                {"role": "user", "content": q}
            ],
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- 🔊 4. Smart Voice Engine (Language Detection) ---
def speak(text):
    try:
        short_text = text[:200] 
        # தமிழில் எழுத்துக்கள் இருக்கிறதா என்று பார்க்கிறோம்
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', short_text))
        lang_code = 'ta' if is_tamil else 'en'
        
        tts = gTTS(text=short_text, lang=lang_code) 
        tts.save("response.mp3")
        return "response.mp3"
    except:
        return None

# --- 🚀 5. Main Interaction Logic ---
st.info("💡 **Tip:** Click the microphone to ask questions in Tamil or English.")

# Voice Input Section
voice_data = speech_to_text(
    start_prompt="🎤 Click to Ask via Voice",
    stop_prompt="🛑 Stop Recording",
    language='ta-IN', 
    use_container_width=True,
    key='final_aipsss_mic'
)

# Text Input Section
text_data = st.chat_input("Type your question here...")

# Logic to determine input source
prompt = voice_data if voice_data else text_data
is_voice = True if voice_data else False

if prompt:
    with st.chat_message("user"):
        st.markdown(f"**Query:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            reply = ai_response(prompt)
            st.success(reply)
            
            # மைக் மூலம் கேள்வி கேட்டால் மட்டும் ஆடியோ தானாக ஒலிக்கும்
            if is_voice:
                audio_path = speak(reply)
                if audio_path:
                    st.audio(audio_path, autoplay=True)
