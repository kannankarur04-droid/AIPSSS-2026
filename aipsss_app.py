import streamlit as st
from groq import Groq
import os
import base64

# --- 🔐 1. Groq Setup ---
# உங்கள் Groq API Key-ஐ இங்கே கொடுக்கவும்
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    # ஒருவேளை secrets-ல் இல்லையென்றால் நேரடியாக இங்கே கொடுக்கலாம்
    client = Groq(api_key="உங்கள்_GROQ_API_KEY_இங்கே")

# --- 🎨 2. Styling (CSS) - 'Final Logo' Design ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1100px; }

    /* ஹெட்டர் பெட்டி - கறுப்பு பின்னணி */
    .header-banner {
        display: flex;
        flex-direction: row;
        align-items: flex-end; /* வரிகளை லோகோவின் காலுக்கு நேராகக் கொண்டு வர */
        background-color: #000000;
        padding: 15px 25px;
        border-radius: 15px;
        gap: 25px;
        margin-bottom: 25px;
    }

    /* லோகோ அளவு */
    .logo-img {
        width: 140px !important; 
        height: auto;
    }

    /* எழுத்துக்கள் தொகுப்பு */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding-bottom: 5px;
    }

    /* தலைப்பு - சிகப்பு & கேப்பிடல் (நீங்கள் கேட்ட 50px அளவு) */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 50px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; 
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* வாசகம் - வெள்ளை */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 18px !important;
        color: #FFFFFF !important; 
        margin: 6px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* டெவலப்பர் - தங்கம் & நீங்கள் கேட்ட அந்த லைன் ஸ்பேஸ் */
    .developer-tag {
        font-family: 'Lexend', sans-serif;
        font-size: 14px !important;
        color: #FFD700 !important; 
        margin-top: 12px !important; 
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* மொபைல் போன் அலைன்மென்ட் - பக்கவாட்டில் வர */
    @media only screen and (max-width: 600px) {
        .header-banner { flex-direction: row !important; gap: 12px; padding: 10px; }
        .logo-img { width: 80px !important; }
        .main-title { font-size: 20px !important; }
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Display Logic ---
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    st.markdown(f'''
        <div class="header-banner">
            <img src="data:image/png;base64,{base64_img}" class="logo-img">
            <div class="header-text">
                <h1 class="main-title">AI Student Support System</h1>
                <p class="main-tagline">"Everyone has the right to education"</p>
                <p class="developer-tag">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 📜 5. Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🚀 6. Main Logic (Groq Engine) ---
prompt = st.chat_input("Ask your educational doubt...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.1
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
