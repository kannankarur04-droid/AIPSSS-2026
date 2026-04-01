import streamlit as st
from groq import Groq
import os
import base64

# --- 🔐 1. Groq Setup ---
# ஒருவேளை secrets-ல் இல்லையென்றால் உங்கள் API Key-ஐ இங்கே நேரடியாகக் கொடுக்கலாம்
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    # உதாரணமாக: client = Groq(api_key="gsk_your_key_here")
    st.error("GROQ_API_KEY காணவில்லை!")
    st.stop()

# --- 🎨 2. Styling (CSS) - ALL FIXES INCLUDED ---
st.set_page_config(page_title="AIPSSS - AI STUDENT MENTOR", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    /* கறுப்பு பின்னணி மற்றும் முழு பக்க வடிவமைப்பு */
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1100px; }

    /* ஹெட்டர் பெட்டி - கறுப்பு செவ்வகம் */
    .header-banner {
        display: flex;
        flex-direction: row;
        align-items: flex-end; 
        background-color: #000000;
        padding: 20px 30px;
        border-radius: 15px;
        gap: 30px;
        margin-bottom: 30px;
        border: 1px solid #333;
    }

    /* லோகோ அளவு */
    .logo-img { 
        width: 150px !important; 
        height: auto; 
    }

    /* எழுத்துக்கள் தொகுப்பு - இடது பக்கம் கச்சிதமான நேர்க்கோடு (Left-aligned) */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: flex-start; /* அனைத்து வரிகளையும் இடது பக்கம் நேராக அடுக்க */
        padding-bottom: 5px;
        text-align: left;
    }

    /* தலைப்பு - சிகப்பு நிறம் (50px) & கேப்பிடல் லெட்டர்ஸ் */
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

    /* வாசகம் - வெள்ளை நிறம் */
    .main-tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 19px !important;
        color: #FFFFFF !important; 
        margin: 8px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* டெவலப்பர் - தங்கம் (Gold) & நீங்கள் கேட்ட அந்த இடைவெளி */
    .developer-tag {
        font-family: 'Lexend', sans-serif;
        font-size: 15px !important;
        color: #FFD700 !important; 
        margin-top: 15px !important; /* கூடுதல் இடைவெளி */
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* மொபைல் போன் அலைன்மென்ட் - பக்கவாட்டில் சீராக வர */
    @media only screen and (max-width: 600px) {
        .header-banner { flex-direction: row !important; gap: 12px; padding: 10px; }
        .logo-img { width: 85px !important; }
        .main-title { font-size: 20px !important; letter-spacing: -0.5px; }
        .main-tagline { font-size: 11px !important; }
        .developer-tag { font-size: 10px !important; margin-top: 8px !important; }
    }

    /* கேள்வி பெட்டி டிசைன் */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History Setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Display Logic ---
# படம் GitHub-ல் 'aipsss_robot_final.png' என்ற பெயரில் இருப்பதை உறுதி செய்யவும்
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
    # படம் லோட் ஆகவில்லை என்றால் மாற்றுத் தலைப்பு
    st.markdown('<div class="header-banner"><h1 class="main-title">AI STUDENT SUPPORT SYSTEM</h1></div>', unsafe_allow_html=True)

# --- 📜 5. Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🚀 6. Main Interaction (Groq Engine) ---
prompt = st.chat_input("உங்களின் கல்வி சந்தேகங்களைக் கேட்கவும்...")

if prompt:
    # பயனர் செய்தி
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # அசிஸ்டண்ட் பதில்
    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            try:
                # Groq மூலம் பதில் பெறுதல்
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.3
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"மன்னிக்கவும், ஒரு பிழை ஏற்பட்டுள்ளது: {e}")
