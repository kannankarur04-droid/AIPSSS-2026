import streamlit as st
import google.generativeai as genai
import time
import re
from gtts import gTTS
import os

# 🔐 API Key Setup (Secrets-ல் இருந்து பாதுகாப்பாக எடுக்கும்படி மாற்றியுள்ளேன்)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS Voice", layout="wide", page_icon="🎓")
st.title("🎓 AI Student Support (Voice Enabled)")

# 💾 Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📜 பழைய மெசேஜ்களைக் காட்டுதல்
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ Input Box
prompt = st.chat_input("Type your question here...")

# ➕ கணக்குகளைச் சரிசெய்யும் பங்க்ஷன்
def solve_math(q):
    q_clean = q.replace("=", "").strip()
    if re.match(r'^[0-9+\-*/.() ]+$', q_clean):
        try:
            return str(eval(q_clean))
        except:
            return None
    return None

# 🤖 AI பதில் சொல்லும் பகுதி
def ai_response(q):
    try:
        # முதலில் 1.5 flash முயற்சிக்கும்
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(q)
        return res.text
    except Exception as e:
        try:
            # அது வேலை செய்யவில்லை என்றால் gemini-pro முயற்சிக்கும்
            model = genai.GenerativeModel("gemini-pro")
            res = model.generate_content(q)
            return res.text
        except:
            return f"⚠️ Error: {str(e)}"

# 🔊 ஆடியோவாக மாற்றும் பகுதி
def speak(text):
    try:
        # நீளமான பதில்களைச் சுருக்கி ஆடியோவாக மாற்றுகிறது
        short_text = text[:200] 
        tts = gTTS(text=short_text, lang='en')
        tts.save("output.mp3")
        return "output.mp3"
    except Exception as e:
        return None

# 🚀 Main Logic
if prompt:
    user_q = prompt.lower().strip()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None
    
    # 1. கணக்கா என்று பார்த்தல்
    math_result = solve_math(user_q)
    
    if math_result:
        reply = f"The answer is {math_result}"
    else:
        # 2. மற்ற கேள்விகளுக்கு AI பதில்
        with st.spinner("Thinking..."):
            reply = ai_response(prompt)

    with st.chat_message("assistant"):
        st.markdown(reply)
        
        # 3. பதிலை ஆடியோவாக ஒலிக்கச் செய்தல்
        audio_file = speak(reply)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            # பழைய ஆடியோ கோப்புகளை நீக்குதல் (தேவைப்பட்டால்)

    st.session_state.messages.append({"role": "assistant", "content": reply})
