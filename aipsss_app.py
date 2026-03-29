import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re

# --- 🔐 1. Groq API Key Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY! Please check Streamlit Secrets.")
    st.stop()

# --- 🎨 2. UI Configuration ---
st.set_page_config(page_title="AI Student Support", layout="wide", page_icon="🎓")
st.title("🎓 AI Powered Student Support System")
st.markdown("### *Your Secure & Intelligent Educational Assistant*")
st.write("---")

# --- 🧠 3. AI Core Logic (Short & Direct Safety Response) ---
def ai_response(q):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """
                    You are a STRICT EDUCATIONAL ASSISTANT. 
                    - RULES:
                      1. Respond ONLY to educational queries (Science, Math, History, etc.).
                      2. If the user asks about movies, politics, games, or celebrities, respond ONLY with: 'மன்னிக்கவும், நான் ஒரு கல்வி உதவியாளர். கல்வி சார்ந்த கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்.'
                      3. Do not give any extra advice or explanations for restricted topics.
                      4. Follow language and line limit rules strictly.
                    """
                },
                {"role": "user", "content": q}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- 🔊 4. Smart Voice Engine ---
def speak(text):
    try:
        short_text = text[:250] 
        is_tamil = bool(re.search(r'[\u0b80-\u0bff]', short_text))
        lang_code = 'ta' if is_tamil else 'en'
        
        tts = gTTS(text=short_text, lang=lang_code) 
        tts.save("response.mp3")
        return "response.mp3"
    except:
        return None

# --- 🚀 5. Main Interaction Logic ---
st.info("💡 **Educational Use Only:** Ask about Science, History, Math, or Languages.")

voice_data = speech_to_text(
    start_prompt="🎤 Click to Ask via Voice",
    stop_prompt="🛑 Stop Recording",
    language='ta-IN', 
    use_container_width=True,
    key='final_secure_mic'
)

text_data = st.chat_input("Ask an educational question...")

prompt = voice_data if voice_data else text_data
is_voice = True if voice_data else False

if prompt:
    with st.chat_message("user"):
        st.markdown(f"**Query:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner("Analyzing educational query..."):
            reply = ai_response(prompt)
            st.success(reply)
            
            if is_voice:
                audio_path = speak(reply)
                if audio_path:
                    st.audio(audio_path, autoplay=True)
