import streamlit as st
from google import genai
import time
import os
import base64

# --- 🔐 1. API Setup ---
# உங்கள் API Key-ஐ இங்கே கொடுத்துள்ளேன். (பாதுகாப்பிற்கு இதை streamlit secrets-ல் வைப்பது நல்லது)
client = genai.Client(api_key="AIzaSyD5U5-VOb6YchdkSDC6Xi4qRGnc-zablYg")

# --- 🎨 2. Styling (CSS) - 'Final Logo' Design ---
st.set_page_config(page_title="AIPSSS", layout="wide")

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
        font-size: 45px !important; 
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
        margin-top: 12px !important; /* இடைவெளி அதிகரிக்கப்பட்டுள்ளது */
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* மொபைல் போன் அலைன்மென்ட் - பக்கவாட்டில் வர */
    @media only screen and (max-width: 600px) {
        .header-banner { flex-direction: row !important; gap: 12px; padding: 10px; }
        .logo-img { width: 80px !important; }
        .main-title { font-size: 18px !important; }
        .main-tagline { font-size: 10px !important; }
        .developer-tag { font-size: 9px !important; margin-top: 8px !important; }
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Session & Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

SYSTEM_PROMPT = "Explain simply with example. Use formulas if needed. Add 2 MCQs."

# --- 🖼️ 4. Header Display Logic ---
# லோகோ படம் உங்கள் GitHub-ல் 'aipsss_robot_final.png' என்ற பெயரில் இருக்க வேண்டும்
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
else:
    # படம் இல்லையென்றால் வெறும் தலைப்பு மட்டும் தெரியும்
    st.markdown('<h1 style="color:#FF4B4B; text-transform:uppercase;">AI Student Support System</h1>', unsafe_allow_html=True)

# --- 📜 5. Show Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 🔁 6. Function with Gemini 1.5 Flash ---
def get_ai_response(user_prompt):
    for i in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=SYSTEM_PROMPT + "\n\nQ: " + user_prompt
            )
            return response.text if response.text else "No response."
        except Exception:
            time.sleep(5)
    return "⚠️ Server busy. Please try again later."

# --- 🚀 7. Main Logic ---
prompt = st.chat_input("Ask your educational doubt...")

if prompt:
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check cache or call AI
    if prompt in st.session_state.cache:
        reply = st.session_state.cache[prompt]
    else:
        with st.spinner("Thinking..."):
            reply = get_ai_response(prompt)
            st.session_state.cache[prompt] = reply

    # Assistant message
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
