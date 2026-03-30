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
        align-items: center; 
        justify-content: flex-start; /* இடது பக்கம் ஒட்டியிருக்க */
        display: flex;
        gap: 10px; /* லோகோவுக்கும் பெயருக்கும் இடையே சிறிய இடைவெளி */
        margin-top: -30px; /* மேல் இடைவெளியைக் குறைக்க */
    }

    /* AIPSSS Title - சிவப்பு நிறம் */
    .main-title { 
        font-size: 50px !important; 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B;
        letter-spacing: 2px;
        margin: 1; /* மார்ஜினை நீக்கு */
        line-height: 1; /* வரி உயரத்தைச் சுருக்கு */
    }
    
    /* (AI Powered Student Support System) - கேப்ஷன் */
    .main-tagline {
        font-size: 16px !important; 
        text-align: left; 
        color: #555; /* Neutral color for readability */
        margin-top: -5px; /* தலைப்புக்கு நெருக்கமாக வைக்க */
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
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
    }

    /* PDF அப்லோடர் பெட்டி */
    .stFileUploader { margin-top: 20px; }
    
    /* Chat Message bubble style */
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🖼️ 3. Fixed Header Alignment (Logo Left, Text Right) ---
# GitHub-ல் aipsss_robot_final.png என்ற பெயரில் படம் இருப்பதை உறுதி செய்யவும்
img_name = 'aipsss_robot_final.png' 
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
