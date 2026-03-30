import streamlit as st
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import re
from PIL import Image
import fitz  # PyMuPDF

# --- 🔐 1. Setup ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY!")
    st.stop()

# --- 🎨 2. Styling (Advanced CSS for Perfect Alignment) ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* தலைப்பைச் சுருக்க */
    .block-container { padding-top: 1.5rem !important; }
    
    /* லோகோ மற்றும் பெயரை செங்குத்தாக நடுவில் வைக்க */
    [data-testid="stHorizontalBlock"] {
        align-items: center; 
        justify-content: center; /* மொபைலிலும் சென்டராக இருக்க */
        display: flex;
        gap: 15px; /* லோகோவுக்கும் பெயருக்கும் இடையே இடைவெளி */
        margin-top: -30px; /* மேல் இடைவெளியைக் குறைக்க */
    }

    /* AIPSSS Title - Bold Red */
    .main-title { 
        font-size: 52px !important; 
        font-weight: 900; 
        text-align: left; /* காலம்ஸிற்குள் இடது பக்கம் */
        color: #FF4B4B !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }
    
    /* Tagline - Simple & Clear */
    .main-tagline {
        font-size: 18px !important; 
        text-align: left; 
        color: #555; /* Neutral color for readability */
        margin-top: 0px;
        display: block;
        font-weight: bold;
    }
    
    /* மைக் பட்டன் - பெரிய அளவு மற்றும் சிவப்பு நிறம் */
    .stButton > button {
        height: 85px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        background-color: #FF4B4B !important;
        color: white !important;
        border: none;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }

    /* PDF அப்லோடர் பெட்டி */
    .stFileUploader { margin-top: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Fixed Header Placement (Logo & Title Side-by-Side) ---
# கவனிக்கவும்: படத்தின் பெயர் GitHub-ல் 'aipsss_robot.png' என்று இருக்க வேண்டும்
img_name = 'aipsss_robot.png' 
img_path = os.path.join(os.getcwd(), img_name)

# லோகோ மற்றும் தலைப்பை ஒரே வரிசையில் காட்ட (CSS alignments மேலே கொடுத்துள்ளோம்)
try:
    if os.path.exists(img_path):
        logo_img = Image.open(img_path)
        
        # ஸ்ட்ரீம்லிட் காலம்ஸ் - இது ரெஸ்பான்சிவ் ஆக இருக்கும்
        col1, col2 = st.columns([1, 4]) 
        
        with col1:
            # லோகோ அளவு - சுருக்கப்பட்டது
            st.image(logo_img, width=85) 
            
        with col2:
            # தலைப்பு மற்றும் கேப்ஷன் ஒரே பாக்ஸில் இருக்கும்
            st.markdown('<p class="main-title">AIPSSS</p>', unsafe_allow_html=True)
            st.markdown('<p class="main-tagline">AI Powered Student Support System</p>', unsafe_allow_html=True)
            
    else:
        # படம் இல்லையென்றால்Fall Back
        st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555; font-weight:bold;">AI Powered Student Support System</p>', unsafe_allow_html=True)
        # படக் கோப்பு ஏன் வரவில்லை என்ற குறிப்பு அட்மினுக்கு மட்டும்
        # st.warning(f"Note: {img_name} not found in root.")

except:
    st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 4. AI Core ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AIPSSS, a kind Education Assistant. Answer educational doubts briefly (max 4 lines)."},
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# --- 🎙️ 5. Interaction - Voice (Top Priority) ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='v_mic'
)

# --- 🚀 6. Input & PDF (The Order You Asked) ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc: pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 💬 7. Display Output ---
prompt = voice_input if voice_input else text_input
if prompt:
    with st.chat_message("user"): st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("r.mp3")
            st.audio("r.mp3", autoplay=True)
