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

# --- 🎨 2. Styling (CSS) - நெருக்கமான மற்றும் கச்சிதமான வடிவமைப்பு ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* Title Styling */
    .main-title { 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B; 
        letter-spacing: -1px;
        margin: 0 !important; 
        line-height: 0.8 !important; /* வரிகளுக்கு இடையே மிகக் குறைந்த இடைவெளி */
    }
    
    /* Responsive Sizes */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 38px !important; }
        .tagline { font-size: 13px !important; }
        .quote { font-size: 12px !important; }
        .developer { font-size: 11px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 65px !important; }
        .tagline { font-size: 18px !important; }
        .quote { font-size: 16px !important; }
        .developer { font-size: 14px !important; }
    }
    
    /* வரிகளுக்கு இடையே உள்ள இடைவெளியைக் குறைத்தல் */
    .tagline { color: #FFD700; font-weight: bold; margin: 0 !important; line-height: 1.0 !important; padding-top: 4px; }
    .quote { color: #FFD700; font-style: italic; margin: 0 !important; line-height: 1.0 !important; padding-top: 3px; font-weight: 500; }
    .developer { color: #FFFFFF; margin: 0 !important; line-height: 1.0 !important; padding-top: 3px; opacity: 0.9; }
    
    /* Chat & Button Styles */
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; font-size: 20px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic (பெயர்களை லோகோவுடன் ஒட்டி வைத்தல்) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    # gap: 8px - இது பெயர்களை லோகோவிற்கு மிக நெருக்கமாக கொண்டு வரும்
    header_html = f'''
        <div style="display: flex; align-items: flex-end; gap: 8px; margin-top: 30px; margin-bottom: 30px; padding-left: 5px;">
            <img src="data:image/png;base64,{base64_img}" style="width: 210px; height: auto; object-fit: contain; margin-bottom: -5px;">
            <div style="display: flex; flex-direction: column; justify-content: flex-end; padding-bottom: 6px;">
                <p class="main-title">AIPSSS</p>
                <p class="tagline">AI Powered Student Support System</p>
                <p class="quote">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine ---
def ai_response(user_query, pdf_text=""):
    try:
        restricted = ["cinema", "movie", "actor", "adult", "violence", "kill", "fight", "சினிமா", "படம்", "நடிகர்", "பாடல்"]
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும், நான் ஒரு கல்வி வழிகாட்டி. இது போன்ற கேள்விகளுக்கு என்னால் பதில் சொல்ல முடியாது. உங்கள் படிப்பு தொடர்பாக ஏதேனும் உதவி தேவையா?"

        system_instruction = "You are AIPSSS, a helpful and direct Education Assistant. No long lectures. Be professional and natural."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.3)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI & Chat Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_mic_final_v5')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF கோப்புகள்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF இணைக்கப்பட்டது!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
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
