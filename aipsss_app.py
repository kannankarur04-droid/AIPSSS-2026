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

# --- 🎨 2. Styling (CSS) - Mobile Friendly & Responsive ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    /* தலைப்பைச் சுருக்க */
    .block-container { padding-top: 1rem; }
    
    /* லோகோ மற்றும் பெயரை இடதுபுறம் நெருக்கமாக வைக்க (Logo Left, Text Left) */
     [data-testid="stHorizontalBlock"] {
        align-items: center !important; 
        display: flex !important;
        gap: 15px !important;
        margin-top: 0px !important; /* மேலே ஏறுவதைத் தவிர்க்க 0px */
        padding-top: 10px !important;
    }
          /* AIPSSS Title - கம்ப்யூட்டரில் வெட்டப்படாமல் இருக்க திருத்தப்பட்டது */
    .main-title { 
        font-size: 50px !important; 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B;
        letter-spacing: 2px;
        margin: 0 !important; 
        line-height: 1.4 !important; /* இதுதான் தலைப்பு வெட்டப்படுவதைத் தடுக்கும் */
        display: block !important;
        overflow: visible !important;
    }

    /* மொபைலில் 35px */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 35px !important; line-height: 1.2 !important; }
        .main-tagline { font-size: 13px !important; }
    }
    }

    /* கம்ப்யூட்டரில் 50px */
    @media only screen and (min-width: 601px) {
        .main-title {
            font-size: 50px !important;
            line-height: 1.4 !important; /* கம்ப்யூட்டரில் உயரம் அதிகம் தேவை */
            margin: 5px 0;
        }
    }
    
    /* (AI Powered Student Support System) - கேப்ஷன் */
     .main-tagline {
        font-size: 16px !important; 
        text-align: left; 
        color: #555; 
        margin-top: 0px !important;
        line-height: 1.2 !important;
        font-weight: bold;
        display: block;
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
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }

    /* PDF அப்லோடர் பெட்டி */
    .stFileUploader { margin-top: 20px; }
    
    /* Chat Message bubble style */
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ லோகோ மற்றும் தலைப்பு (Fixed for All Screens) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

import base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    if os.path.exists(img_path):
        base64_img = get_base64_image(img_path)
        # லோகோவும் பெயரும் எப்போதும் ஒரே வரிசையில் இருக்க HTML Flexbox
        header_html = f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-top: -30px; margin-bottom: 20px;">
                <img src="data:image/png;base64,{{base64_img}}" style="width: 75px; height: auto;">
                <div style="display: flex; flex-direction: column; justify-content: center;">
                    <p class="main-title" style="margin: 0 !important; line-height: 1.2 !important; font-size: 40px !important;">AIPSSS</p>
                    <p class="main-tagline" style="margin: 0 !important; font-size: 14px !important;">AI Powered Student Support System</p>
                </div>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        # படம் இல்லையென்றால் இங்கே வரும்
        st.markdown('<h1 style="color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)
except Exception as e:
    # ஏதேனும் பிழை ஏற்பட்டால் இங்கே வரும்
    st.markdown('<h1 style="color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

            
    else:
        # படம் இல்லையென்றால்Fall Back
        st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#555; font-weight:bold;">AI Powered Student Support System</p>', unsafe_allow_html=True)
        # படக் கோப்பு ஏன் வரவில்லை என்ற குறிப்பு அட்மினுக்கு மட்டும்
        # st.warning(f"Note: {img_name} not found in root.")

except:
    st.markdown('<h1 style="text-align:center; color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🎙️ 4. Interaction - Voice (Top Priority) ---
voice_input = speech_to_text(
    start_prompt="🎤 பேச இங்கே அழுத்தவும்",
    stop_prompt="🛑 நிறுத்த அழுத்தவும்",
    language='ta-IN',
    use_container_width=True,
    key='aipsss_final_mic'
)

# --- 🧠 5. AI Core Logic (Accuracy Guaranteed) ---
def ai_response(q, pdf_text=""):
    try:
        # PDF தகவலை 1500 எழுத்துக்களுக்குள் சுருக்குகிறோம்
        context = f"PDF Context: {pdf_text[:1500]}" if pdf_text else ""
        
        # 'System' மெசேஜில் துல்லியம் குறித்த கட்டளை சேர்க்கப்பட்டுள்ளது
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": """You are AIPSSS, a highly accurate Education Assistant. 
                    Accuracy is paramount. Double-check mathematical and factual data before answering."""
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {q}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- ⌨️ 6. Input & PDF (Bottom Placement) ---
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")

# PDF அப்லோடர் கீழே
uploaded_pdf = st.file_uploader("📂 கோப்புகள் மூலம் தேட (PDF)", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    for page in doc:
        pdf_context += page.get_text()
    st.success("✅ PDF இணைக்கப்பட்டுள்ளது!")

# --- 🚀 7. Process & Display Output ---
prompt = voice_input if voice_input else text_input

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("யோசிக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.success(reply)
            
            # ஆடியோ பதில் (Audio Response)
            is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
            tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", autoplay=True)
