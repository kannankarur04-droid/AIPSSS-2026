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
st.set_page_config(page_title="AI Student Support System", layout="centered", page_icon="🤖")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Header Banner */
    .header-banner {
        display: flex;
        align-items: flex-end;
        background-color: #000000;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
    }

    /* Logo - BIG SIZE & NO GAP */
    .logo-img {
        width: 200px;
        height: auto;
        margin-right: 5px !important; /* இடைவெளி குறைக்கப்பட்டுள்ளது */
    }

    /* Text Column - TIGHT LINE SPACING & BOTTOM ALIGNMENT */
.header-text {
    display: flex;
    flex-direction: column;
    
    /* வரிகள் லோகோவின் அடிப்பகுதிக்கு நேராக வர 'flex-end' சிறந்தது */
    justify-content: flex-end; 
    
    /* மூன்று வரிகளுக்கு இடையே உள்ள இடைவெளியைக் குறைக்க (முக்கியம்!) */
    gap: 2px; 
    
    /* வரிகள் பெட்டியின் ஓரத்தோடு ஒட்டாமல் இருக்க */
    padding-bottom: 10px; 
}

/* வரிகளுக்குள் இருக்கும் கூடுதல் இடைவெளியை நீக்க */
.header-text h1, .header-text p {
    margin: 0 !important;
    line-height: 1.0 !important;
}

    .main-title { 
        font-size: 32px !important; 
        font-weight: 900; 
        color: #FF4B4B; 
        margin: 0 !important;
        line-height: 0.9 !important; /* நெருக்கமான இடைவெளி */
        letter-spacing: -1px;
    }

    .main-tagline {
        font-size: 18px !important;
        font-style: italic;
        color: #E0E0E0;
        margin: 2px 0 !important; /* மிகக் குறைந்த இடைவெளி */
        line-height: 1 !important;
    }

    .developer-tag {
        font-size: 16px !important;
        color: #FFD700; 
        font-weight: bold;
        margin: 18x !important;
        line-height: 1 !important;
    }

    @media only screen and (max-width: 600px) {
        .header-banner { flex-direction: row; padding: 10px; }
        .logo-img { width: 100px; }
        .main-title { font-size: 28px !important; }
        .main-tagline { font-size: 12px !important; }
        .developer-tag { font-size: 11px !important; }
    }

    .stButton > button {
        border-radius: 10px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic ---
img_name = 'final logo.jpg' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        header_html = f'''
            <div class="header-banner">
    <img src="YOUR_IMAGE_DATA" class="logo-img">
    
    <div class="header-text">
        <h1 class="main-title">AI STUDENT SUPPORT SYSTEM</h1>
        <p class="main-tagline">"Everyone has the right to education"</p>
        <p class="developer-tag">Developed by Brammadevan</p>
    </div>
</div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
except:
    st.title("AI Student Support System")

# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic_v3'
)

# --- 🧠 5. AI Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AI Assistant. Help students with their education questions."},
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
