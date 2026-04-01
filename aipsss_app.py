import streamlit as st
from groq import Groq
import os
import base64

# --- 🔐 1. Groq Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    # ஒருவேளை எரர் வந்தால் உங்கள் API Key-ஐ இங்கே கொடுக்கலாம்
    client = Groq(api_key="YOUR_GROQ_API_KEY")

# --- 🎨 2. Styling (CSS) ---
st.set_page_config(page_title="AI STUDENT MENTOR", layout="wide")

# CSS வரிகளை st.markdown(""" ... """) குறியீட்டிற்குள் வைப்பதால்தான் அவை திரையில் தெரியாமல் டிசைனாக மாறும்
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1100px; }

    /* ஹெட்டர் பேனர் - கறுப்பு பெட்டி */
    .header-banner {
        display: flex;
        flex-direction: row;
        align-items: flex-end; 
        background-color: #000000;
        padding: 20px 30px;
        border-radius: 15px;
        gap: 25px;
        margin-bottom: 25px;
        border: 1px solid #333;
    }

    /* லோகோ அளவு */
    .logo-img { width: 150px !important; height: auto; }

    /* எழுத்துக்கள் பெட்டி - இடது பக்கம் நேராக அடுக்க */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: flex-start;
        text-align: left;
        padding-bottom: 5px;
    }

    /* தலைப்பு - 50px சிகப்பு & கேப்பிடல் */
    .main-title {
        font-family: 'Lexend', sans-serif;
        font-size: 50px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.85 !important; 
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* வாசகம் - வெள்ளை */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 19px !important;
        color: #FFFFFF !important; 
        margin: 8px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* டெவலப்பர் - தங்கம் & நீங்கள் கேட்ட இடைவெளி */
    .developer-tag {
        font-family: 'Lexend', sans-serif;
        font-size: 15px !important;
        color: #FFD700 !important; 
        margin-top: 15px !important; 
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* மொபைல் போன் அலைன்மென்ட் */
    @media only screen and (max-width: 600px) {
        .header-banner { flex-direction: row !important; gap: 12px; padding: 10px; }
        .logo-img { width: 85px !important; }
        .main-title { font-size: 20px !important; letter-spacing: -0.5px; }
        .main-tagline { font-size: 11px !important; }
        .developer-tag { font-size: 10px !important; }
    }

    /* சாட் இன்புட் */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic ---
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
    st.markdown('<div class="header-banner"><h1 class="main-title">AI STUDENT SUPPORT SYSTEM</h1></div>', unsafe_allow_html=True)

# --- 📜 4. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🚀 5. AI Interaction ---
prompt = st.chat_input("உங்களின் சந்தேகங்களைக் கேட்கவும்...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.3
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
