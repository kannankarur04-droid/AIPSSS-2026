import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF
import base64

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Ultra Tight Spacing ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    
    /* Header Container */
    .aipsss-header {
        display: flex;
        align-items: flex-end; 
        justify-content: flex-start;
        gap: 12px; 
        margin-bottom: 30px;
        margin-top: 20px;
        width: 100%;
    }

    /* Logo Size - Large */
    .main-logo {
        width: 250px; 
        height: auto;
        object-fit: contain;
    }

    /* Content Box - Line spacing optimized */
    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        text-align: left;
    }

    /* Desktop View */
    @media (min-width: 769px) {
        .main-logo { width: 250px; }
        .main-title { font-size: 4.8rem !important; line-height: 0.75 !important; }
        .subtitle { font-size: 1.6rem !important; line-height: 0.9 !important; }
        .quote-text { font-size: 1.15rem !important; line-height: 0.9 !important; }
        .developer { font-size: 1rem !important; line-height: 0.9 !important; }
    }

    /* Mobile View */
    @media (max-width: 768px) {
        .aipsss-header { gap: 8px; flex-wrap: nowrap; align-items: center; }
        .main-logo { width: 100px !important; }
        .main-title { font-size: 2.3rem !important; line-height: 0.8 !important; }
        .subtitle { font-size: 0.85rem !important; line-height: 0.95 !important; }
        .quote-text { font-size: 0.75rem !important; line-height: 0.95 !important; }
        .developer { font-size: 0.7rem !important; line-height: 0.95 !important; }
    }

    /* Text Colors & Styles */
    .main-title { font-weight: 900 !important; color: #ff4d4d !important; margin: 0 !important; letter-spacing: -2px; }
    .subtitle { color: #FFD700 !important; margin: 0 !important; font-weight: bold !important; padding-top: 2px !important; }
    .quote-text { font-style: italic !important; color: #FFD700 !important; margin: 0 !important; padding-top: 1px !important; }
    .developer { color: #FFFFFF !important; opacity: 0.8 !important; margin: 0 !important; padding-top: 1px !important; }

    /* UI Styles */
    .stButton > button { height: 70px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine (Strictly Educational) ---
def ai_response(user_query, pdf_text=""):
    try:
        # Gaming & Illegal Block Filter
        forbidden = ["game", "gaming", "play", "pubg", "free fire", "cheat", "hack", "illegal", "movie", "song", "actor", "விளையாட்டு", "கேம்", "சினிமா", "படம்"]
        
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும் கண்ணன், நான் ஒரு கல்வி உதவியாளர். படிப்பு மற்றும் வேலைவாய்ப்பு தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதில் அளிக்க முடியும்."

        system_instruction = "You are AIPSSS, a strict Education Assistant. Only answer academic and career queries. Refuse entertainment topics."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1000]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_v24_tight')
text_input = st.chat_input("கல்வி தொடர்பான கேள்வியைக் கேட்கவும்...")
uploaded_pdf = st.file_uploader("📂 கல்வி சார்ந்த PDF", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF Ready!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
