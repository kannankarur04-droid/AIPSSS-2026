import streamlit as st
from groq import Groq
import os
import base64

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (The "Perfect Alignment" Design) ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* பின்னணி மற்றும் மெயின் கண்டெய்னர் */
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 900px; }

    /* ஹெட்டர் அமைப்பு - முழுமையாக மாற்றப்பட்டுள்ளது */
    .custom-header {
        display: flex;
        align-items: flex-end; /* பெட்டியின் மேல் கால் வைப்பது போன்ற தோற்றம் */
        gap: 20px;
        margin-bottom: -15px; /* கேள்வி பெட்டியுடன் இணைக்க */
        padding-left: 10px;
    }

    /* லோகோ - பெட்டியை மிதிப்பது போன்ற அலைன்மென்ட் */
    .main-logo {
        width: 180px !important; 
        height: auto;
        margin-bottom: -10px; /* காலுக்கும் பெட்டிக்கும் இடைவெளி குறைக்க */
        z-index: 10;
    }

    /* எழுத்துக்கள் பெட்டி - நெருக்கமான இடைவெளிகள் */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding-bottom: 25px; /* வரிகளைப் பெட்டியின் மேலிருந்து சற்று உயர்த்த */
    }

    /* AI STUDENT MENTOR - RED */
    .main-title {
        font-size: 52px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; /* மிக நெருக்கமான வரி */
        text-transform: uppercase;
    }

    /* Tagline - White */
    .subtitle {
        font-size: 20px !important;
        color: #FFFFFF !important; 
        margin: 8px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* Developer - Gold */
    .developer {
        font-size: 16px !important;
        color: #FFD700 !important; 
        margin: 5px 0 0 0 !important;
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* கேள்வி பெட்டி ஸ்டைல் (Chat Input) */
    .stChatInputContainer {
        border-radius: 15px !important;
        border-top: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* மொபைல் சீரமைப்பு */
    @media (max-width: 768px) {
        .main-title { font-size: 28px !important; }
        .main-logo { width: 100px !important; }
        .custom-header { gap: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Display Logic (Fixed & Tested) ---
base64_img = None 
img_path = os.path.join(os.getcwd(), 'aipsss_robot_final.png')

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    st.markdown(f'''
        <div class="custom-header">
            <img src="data:image/png;base64,{base64_img}" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AI STUDENT MENTOR</h1>
                <p class="subtitle">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

# --- 🤖 4. Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

prompt = st.chat_input("கேள்வியைக் கேட்கவும்...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        # எளிய பதில் (டெஸ்ட் செய்ய)
        res = f"வணக்கம் கண்ணன்! உங்கள் கேள்வி: {prompt}. இதற்கான கல்வி தகவல்களைத் தேடுகிறேன்."
        st.markdown(res)
    st.session_state.messages.append({"role": "assistant", "content": res})
