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

# --- 🎨 2. Styling (CSS) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    .main-title { 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B;
        letter-spacing: 1px;
        margin: 0 !important; 
        display: block !important;
        overflow: visible !important;
    }

    /* Responsive Sizes */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 35px !important; line-height: 1.1 !important; }
        .main-tagline { font-size: 14px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 55px !important; line-height: 1.1 !important; }
        .main-tagline { font-size: 18px !important; }
    }
    
    .main-tagline {
        text-align: left; 
        color: #555; 
        margin-top: 5px !important;
        line-height: 1.2 !important;
        font-weight: bold;
        display: block;
    }
    
    .stButton > button {
        height: 75px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 20px !important;
        background-color: #FF4B4B !important;
        color: white !important;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic (Logo Enlarged & Aligned) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        # லோகோ அளவு 150px ஆக அதிகரிக்கப்பட்டுள்ளது
        header_html = f'''
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
                <img src="data:image/png;base64,{base64_img}" style="width: 150px; height: auto; object-fit: contain;">
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <p class="main-title">AIPSSS</p>
                    <p class="main-tagline">AI Powered Student Support System</p>
                    <p style="font-size: 12px; color: #888; margin: 0;">Developed by Kannan</p>
                </div>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.markdown('<h1 style="color:#FF4B4B; margin:0;">AIPSSS</h1>', unsafe_allow_html=True)
except Exception:
    st.markdown('<h1 style="color:#FF4B4B; margin:0;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_mic_v2')

# --- 🧠 5. AI Core Logic (Safety & Career Focus Included) ---
def ai_response(q, pdf_text=""):
    try:
        restricted_keywords = ["cinema", "movie", "game", "pubg", "freefire", "illegal", "adult", "சினிமா", "படம்"]
        if any(word in q.lower() for word in restricted_keywords):
            return "மன்னிக்கவும், நான் கல்வி மற்றும் வேலைவாய்ப்பு தொடர்பான உதவிகளை மட்டுமே வழங்க முடியும்."

        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        system_instruction = "You are AIPSSS, a dedicated Educational and Career Assistant. Help with exams, job prep, and studies. Avoid entertainment topics."
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- ⌨️ 6. Input & PDF ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 🚀 7. Output ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    
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
