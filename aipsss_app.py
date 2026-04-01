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
st.set_page_config(page_title="AI Student Mentor", layout="centered", page_icon="🤖")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    
    /* Header Container */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }

    /* Logo Style */
    .logo-img {
        width: 100px;
        height: auto;
    }

    /* Text Content */
    .header-text {
        display: flex;
        flex-direction: column;
    }

    .main-title { 
        font-size: 42px !important; 
        font-weight: 900; 
        color: #FF4B4B; 
        margin: 0 !important;
        line-height: 1.1 !important;
        text-transform: uppercase;
    }

    .main-tagline {
        font-size: 18px !important;
        font-style: italic;
        color: white;
        margin: 5px 0 !important;
    }

    .developer-tag {
        font-size: 14px !important;
        color: #FFD700; /* Yellow color */
        font-weight: bold;
        margin: 0 !important;
    }

    /* Mobile responsiveness */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 28px !important; }
        .main-tagline { font-size: 14px !important; }
        .logo-img { width: 70px; }
    }

    /* Button & Chat UI */
    .stButton > button {
        border-radius: 12px !important;
        background-color: #FF4B4B !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic ---
# உங்கள் லோகோ கோப்பு பெயர் 'final logo.jpg' என இருப்பதை உறுதி செய்யவும்
img_name = 'final logo.jpg' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        header_html = f'''
            <div class="header-container">
                <img src="data:image/jpeg;base64,{base64_img}" class="logo-img">
                <div class="header-text">
                    <p class="main-title">AI STUDENT MENTOR</p>
                    <p class="main-tagline">"Everyone has the right to education"</p>
                    <p class="developer-tag">Developed by Brammadevan</p>
                </div>
            </div>
        '''
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.error("Logo file not found! Please check 'final logo.jpg' path.")
except Exception as e:
    st.markdown('<h1 style="color:#FF4B4B;">AI STUDENT MENTOR</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction - Voice ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_mic_v2'
)

# --- 🧠 5. AI Core Logic ---
def ai_response(q, pdf_text=""):
    try:
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "You are AI Student Mentor, a helpful Education Assistant. Keep answers concise and supportive."},
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
            
            # Audio Output
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
