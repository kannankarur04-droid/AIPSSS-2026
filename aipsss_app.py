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
st.markdown("### *Your Intelligent Bilingual Learning Assistant*")
st.write("---")

# --- 🧠 3. AI Core Logic (Strict Instructions) ---
def ai_response(q):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """
                    You are a professional bilingual student assistant. 
                    - RULES: 
                      1. Respond ONLY in English if the query is in English. 
                      2. Respond ONLY in Tamil if the query is in Tamil. 
                      3. STRICTLY follow the line limit requested by the user (e.g., '4 lines' means exactly 4 sentences/lines). 
                      4. Do not define the number; explain the topic instead.
                      5. If user says 'Vanakkam' or 'வணக்கம்', reply 'வணக்கம் கண்ணன்! நான் உங்களுக்கு இன்று எப்படி உதவ முடியும்?'.
                      6. Keep all other responses brief and educational.
                    """
                },
                {"role": "user", "content": q}
            ],
            temperature=0.1  # Low temperature for strict instruction following
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
st.info("💡 **Tip:** Click the microphone to ask questions. You can specify line limits (e.g., 'Explain AI in 4 lines').")

voice_data = speech_to_text(
    start_prompt="🎤 Click to Ask via Voice",
    stop_prompt="🛑 Stop Recording",
    language='ta-IN', 
    use_container_width=True,
    key='final_v3_mic'
)

text_data = st.chat_input("Type your question here (e.g., Explain Physics in 3 lines)...")

prompt = voice_data if voice_data else text_data
is_voice = True if voice_data else False

if prompt:
    with st.chat_message("user"):
        st.markdown(f"**Query:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            reply = ai_response(prompt)
            st.success(reply)
            
            if is_voice:
                audio_path = speak(reply)
                if audio_path:
                    st.audio(audio_path, autoplay=True)
