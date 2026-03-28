import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# 🔐 ஏபிஐ கீ (Secrets-ல் இருந்து)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

# 🎨 லோகோ மற்றும் டைட்டில் அமைப்புகள்
st.set_page_config(page_title="AIPSSS Expert", layout="wide", page_icon="🎓")

# 🔵 வண்ணங்கள் மற்றும் தலைப்பு (எளிமையான முறை)
st.markdown("<h1 style='text-align: center; color: #0047AB;'>🎓 ஏஐ மாணவர் ஆதரவு அமைப்பு (AIPSSS)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>உங்கள் கல்வி சந்தேகங்களை இங்கே கேளுங்கள்</p>", unsafe_allow_html=True)

# 💾 மெமரி
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🤖 ஏஐ பதில் சொல்லும் பகுதி
def ai_response(q):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # பதில் தமிழிலேயே வர கட்டளை
        res = model.generate_content("Give a simple 3-line answer in Tamil: " + q)
        return res.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🔊 தமிழ் ஆடியோ
def speak(text):
    try:
        short_text = text[:150]
        tts = gTTS(text=short_text, lang='ta')
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# 🚀 மெயின் லாஜிக்
prompt = st.chat_input("உங்களுடைய கேள்வியை இங்கே கேட்கவும்...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt)
            # பதில் வரும் பெட்டிக்கு ஒரு நீல நிறம்
            st.info(reply)
            
            audio_file = speak(reply)
            if audio_file:
                st.audio(audio_file)

    st.session_state.messages.append({"role": "assistant", "content": reply})
