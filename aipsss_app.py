import streamlit as st
from google import genai
import time
import re
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# 🔑 API
client = genai.Client(api_key="YOUR_API_KEY")

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

prompt = None

if audio:
    st.audio(audio["bytes"])
    prompt = "Voice input detected (convert externally)"  # placeholder

# ⌨️ Text input
text_input = st.chat_input("Type your question...")
if text_input:
    prompt = text_input

# ➕ Math
def solve_math(q):
    q = q.replace(" ", "")
    if re.match(r'^[0-9+\-*/.]+$', q):
        try:
            return str(eval(q))
        except:
            return None
    return None

# 🤖 AI
def ai_response(q):
    try:
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=q
        )
        return res.text
    except:
        return None

# 🔊 Text to Voice
def speak(text):
    tts = gTTS(text)
    tts.save("output.mp3")
    return "output.mp3"

# 🚀 MAIN
if prompt:

    user_q = prompt.lower().strip()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = None

    # Math
    if solve_math(user_q):
        reply = f"Answer: {solve_math(user_q)}"

    # Offline
    elif user_q in OFFLINE_DB:
        reply = OFFLINE_DB[user_q]

    # AI
    else:
        with st.spinner("Thinking..."):
            time.sleep(2)
            reply = ai_response(prompt)

    if not reply:
        reply = "⚠️ AI busy. Try again."

    # Show text
    with st.chat_message("assistant"):
        st.markdown(reply)

    # 🔊 Voice output
    audio_file = speak(reply)
    st.audio(audio_file)

    st.session_state.messages.append({"role": "assistant", "content": reply})
