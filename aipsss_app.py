import streamlit as st
import google.generativeai as genai # லைப்ரரியை மாற்றியுள்ளேன்
import time
import re
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# 🔑 API Setup
# உங்கள் API Key-ஐ இங்கே சரியாகக் கொடுக்கவும்
genai.configure(api_key="YOUR_API_KEY") 

st.set_page_config(page_title="AIPSSS Voice", layout="wide")
st.title("🎓 AI Student Support (Voice Enabled)")

# 💾 Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📚 Basic DB
OFFLINE_DB = {
    "what is computer": "A computer is an electronic device that processes data.",
    "what is commerce": "Commerce is buying and selling of goods and services.",
    "what is ai": "Artificial Intelligence is intelligence shown by machines.",
}

# 📜 Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🎤 Voice Input
st.subheader("🎤 Speak your question")
audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording")

# ⌨️ Text input (ஒரே இடத்தில் Prompt-ஐ வாங்க வசதியாக)
text_input = st.chat_input("Type your question...")

prompt = None
if text_input:
    prompt = text_input
elif audio:
    # Voice input placeholder (நிஜமான தட்டச்சுக்கு பதில் இது செயல்படும்)
    prompt = "Voice input recorded" 

# ➕ Math Function
def solve_math(q):
    # எண்கள் மற்றும் குறிகளை மட்டும் அனுமதிக்கும் Regex
    q_clean = q.replace("=", "").strip()
    if re.match(r'^[0-9+\-*/.() ]+$', q_clean):
        try:
            return str(eval(q_clean))
        except:
            return None
    return None

# 🤖 AI Function (Updated)
def ai_response(q):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash") # நிலைத்தன்மைக்காக 1.5 Flash
        res = model.generate_content(q)
        return res.text
    except Exception as e:
        return f"Error: {str(e)}" # பிழையைத் தெளிவாகக் காட்டும்

# 🔊 Text to Voice
def speak(text):
    try:
        tts = gTTS(text)
        tts.save("output.mp3")
        return "output.mp3"
    except:
        return None

# 🚀 MAIN LOGIC
if prompt:
    user_q = prompt.lower().strip()
    
    # பயனர் கேள்வியைக் காட்டுதல்
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None
    
    # 1. முதலில் கணிதத்தைச் சரிபார்க்கவும்
    math_result = solve_math(user_q)
    
    if math_result:
        reply = f"The answer is {math_result}"
    
    # 2. பிறகு Offline DB
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]
    
    # 3. இறுதியாக AI
    else:
        with st.spinner("Thinking..."):
            reply = ai_response(prompt)

    # பிழை செய்தி காட்டாமல் இருக்க
    if not reply:
        reply = "சற்று காத்திருக்கவும். மீண்டும் முயற்சிக்கவும்."

    # பதிலைக் காட்டுதல்
    with st.chat_message("assistant"):
        st.markdown(reply)
        
        # ஆடியோ அவுட்புட்
        audio_file = speak(reply)
        if audio_file:
            st.audio(audio_file)

    st.session_state.messages.append({"role": "assistant", "content": reply})
