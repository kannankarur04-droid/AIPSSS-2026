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
    
    /* Header Container */
    .header-container {
        position: relative;
        margin-top: 20px;
        margin-bottom: 50px; /* கீழ் பக்கம் மிதித்து வருவதால் கூடுதல் இடம் */
        width: 100%;
    }

    /* Black Header Banner - செவ்வகக் கட்டம் */
    .header-banner {
        display: flex;
        align-items: center;
        background-color: #000000;
        padding: 25px 25px 25px 180px; /* படத்தின் அளவுக்கு ஏற்ப இடது பக்கம் கேப் */
        border-radius: 12px;
        min-height: 120px;
        position: relative;
        z-index: 1;
    }

    /* Logo Image - பெரிதாக்கப்பட்டு கீழ் விளிம்பை மிதிப்பது போல */
    .logo-img {
        position: absolute;
        bottom: -25px; /* கட்டத்தின் கீழ் விளிம்பைத் தாண்டி மிதிக்க (Overlap) */
        left: 15px; 
        width: 150px; /* லோகோ பெரிதாக்கப்பட்டுள்ளது */
        height: auto;
        z-index: 10; /* கட்டத்திற்கு மேல் தெரிய */
        filter: drop-shadow(0px 5px 10px rgba(0,0,0,0.5));
    }

    /* Text Column */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .main-title { 
        font-size: 32px !important; 
        font-weight: 900; 
        color: #FF4B4B; 
        margin: 0 !important;
        line-height: 1 !important;
    }

    .main-tagline {
        font-size: 16px !important;
        font-style: italic;
        color: #E0E0E0;
        margin: 5px 0 !important;
        line-height: 1.2 !important;
    }

    .developer-tag {
        font-size: 14px !important;
        color: #FFD700; 
        font-weight: bold;
        margin: 0 !important;
    }

    /* மொபைல் போன்களுக்கான Responsive மாற்றம் */
    @media only screen and (max-width: 768px) {
        .logo-img { 
            width: 100px; 
            bottom: -15px; 
            left: 10px;
        }
        .header-banner { 
            padding: 15px 15px 15px 120px;
            min-height: 100px;
        }
        .main-title { font-size: 18px !important; }
        .main-tagline { font-size: 11px !important; }
        .developer-tag { font-size: 10px !important; }
    }

    .stButton > button {
        border-radius: 10px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Header Logic (Based on image_6.png) ---
img_name = 'final logo.jpg' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f"""
        <div style="display: flex; align-items: flex-start; justify-content: flex-start; padding: 25px 0px; margin-bottom: 30px; width: 100%;">
            <div style="flex: 0 0 auto; margin-right: 30px; margin-top: -10px;">
                <img src="data:image/jpeg;base64,{base64_img}" alt="Logo" style="width: 200px; height: auto;">
            </div>
            
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: flex-start; margin-top: 5px;">
                <p style="font-size: 34px !important; font-weight: 900; color: #FF4B4B; margin: 0 !important; line-height: 1.1 !important; text-transform: uppercase;">
                    AI POWERED STUDENT SUPPORT SYSTEM
                </p>
                
                <p style="font-size: 19px !important; color: #FFFFFF; font-weight: 500; margin: 8px 0 !important; line-height: 1.2 !important;">
                    "Everyone has the right to education"
                </p>
                
                <p style="font-size: 17px !important; color: #FFD700; font-weight: bold; margin: 0 !important; line-height: 1.2 !important;">
                    Developed by Brammadevan
                </p>
            </div>
        </div>
        <hr style="border: 1px solid #333; margin-top: -10px; margin-bottom: 30px;">
    """
    st.markdown(header_html, unsafe_allow_html=True)
else:
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
        # PDF தகவல் இருந்தால் அதைச் சேர்க்கும் பகுதி
        context = f"PDF Context: {pdf_text[:2000]}" if pdf_text else ""
        
        # மாணவர்களுக்கான வழிகாட்டுதல் மற்றும் சுருக்கமான பாதுகாப்பு எச்சரிக்கை
        system_instruction = (
            "You are a 'Comprehensive Student Life Mentor'. Your mission is to guide students through their entire academic and career journey. "
            "COVERAGE AREAS: 1. School Education, 2. College/Higher Education, 3. Competitive Exams (UPSC, TNPSC, NEET, JEE), 4. Skill Development & Career path. "
            "STRICT RESTRICTIONS: 1. No Cinema/Entertainment. 2. No Adult/Illegal content. 3. No Mobile Gaming. 4. Maintain zero bias. "
            "If a user asks about restricted topics, ONLY reply with this exact Tamil sentence: "
            "'மன்னிக்கவும், நான் மாணவர்களுக்கான கல்வி மற்றும் வாழ்க்கை வழிகாட்டி. கல்வி தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்.'"
        )

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
