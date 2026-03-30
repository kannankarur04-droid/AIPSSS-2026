import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (CSS) - Mobile & Mic Friendly ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🎓")

st.markdown("""
    <style>
    /* மொபைல் திரையில் தேவையற்ற இடைவெளியைக் குறைக்க */
    .block-container { padding-top: 2rem; }
    
    /* 🎓 AIPSSS தலைப்பு - சிவப்பு நிறம் */
    .main-title { 
        font-size: 50px !important; 
        font-weight: 900; 
        text-align: center; 
        margin-top: -60px; 
        color: #FF4B4B;
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: -15px; /* விரிவான வாசகத்திற்கு இடம் விட */
    }
    
    /* (AI Powered Student Support System) - Cursive Font */
    .main-tagline {
        font-family: 'Great Vibes', cursive; /* இந்த ஃபான்ட் மொபைலில் அழகாகத் தெரியும் */
        font-size: 20px !important; 
        font-weight: 400; 
        text-align: center; 
        color: #FF4B4B;
        margin-bottom: 25px;
        display: block;
    }
    
    /* மைக் பட்டன் - பெரிய அளவு மற்றும் சிவப்பு நிறம் */
    .stButton > button {
        height: 90px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 24px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF3333 !important;
        transform: scale(1.02);
    }

    /* PDF அப்லோடர் பெட்டி */
    .stFileUploader { margin-top: 15px; }
    
    /* Chat Message Bubble Style */
    .stChatMessage { border-radius: 15px; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Great Vibes&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Title & Tagline Placement (Top) ---
# தலைப்பு மட்டும்
st.markdown('<p class="main-title">🎓 AIPSSS</p>', unsafe_allow_html=True)
# அதன் கீழே Cursive Font-ல் expansion
st.markdown('<p class="main-tagline">(AI Powered Student Support System)</p>', unsafe_allow_html=True)

# --- 🧠 4. AI Logic (Groq Brain) ---
def ai_response(q, pdf_text=""):
    try:
        # PDF தகவலை 1500 எழுத்துக்களுக்குள் சுருக்குகிறோம்
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": "You are AIPSSS, a kind and professional Education Assistant. Answer educational doubts briefly (max 4 lines). Encourage the student."
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction - Voice (Top Priority) ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_final_mic'
)

# --- ⌨️ 6. Interaction - Text & PDF (Bottom Placement) ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# PDF அப்லோடர் - கேள்வி கேட்கும் இடத்திற்கு கீழே
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF-ஐ இங்கே பதிவேற்றவும்)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது. இப்போது கேள்வி கேட்கலாம்!")

# --- 🚀 7. Generate Response ---
prompt = voice_input if voice_input else text_input

if prompt:
    # பயனர் கேள்வி
    with st.chat_message("user"):
        st.write(prompt)
    
    # ஏஐ பதில்
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # ஆடியோ பதில் (gTTS)
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
