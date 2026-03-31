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

# --- 🎨 2. Styling (CSS) - Enhanced Design ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    
    /* Title Styling - Enhanced Size */
    .main-title { 
        font-weight: 900; 
        text-align: left; 
        color: #FF4B4B; /* Red */
        letter-spacing: 1px;
        margin: 0 !important; 
        line-height: 1.0 !important;
    }
    
    /* Responsive Title Sizes */
    @media only screen and (max-width: 600px) {
        .main-title { font-size: 45px !important; }
        .tagline { font-size: 14px !important; }
        .quote { font-size: 13px !important; }
        .developer { font-size: 12px !important; }
    }
    @media only screen and (min-width: 601px) {
        .main-title { font-size: 65px !important; }
        .tagline { font-size: 18px !important; }
        .quote { font-size: 16px !important; }
        .developer { font-size: 14px !important; }
    }
    
    /* 🌟 Gold Color for Tagline & Quote */
    .tagline { 
        text-align: left; 
        color: #FFD700;  /* Gold */
        margin: 0 !important; 
        line-height: 1.2 !important; 
        font-weight: bold; 
        padding-top: 8px; 
    }
    .quote { 
        font-size: 16px; 
        color: #FFD700;  /* Gold */
        font-style: italic; 
        margin: 0 !important; 
        line-height: 1.2 !important; 
        padding-top: quote px; 
        font-weight: 500; 
    }
    
    /* ⚪ White Color for Developer Name */
    .developer { 
        font-size: 14px; 
        color: #FFFFFF;  /* White */
        text-align: left; 
        margin: 0 !important; 
        line-height: 1.2 !important; 
        padding-top: 5px; 
    }
    
    /* Button Style - Responsive */
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

# --- 🧠 3. Chat History (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic (Enlarged Logo & Bottom Aligned Texts) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    # லோகோ அளவு 200px ஆக அதிகரிக்கப்பட்டுள்ளது. 
    # align-items: flex-end வரிகளை லோகோவின் அடிப்பகுதிக்கு நேராக அலைன் செய்யும்.
    header_html = f'''
        <div style="display: flex; align-items: flex-end; gap: 25px; margin-top: 35px; margin-bottom: 30px; padding-left: 10px;">
            <img src="data:image/png;base64,{base64_img}" style="width: 200px; height: auto; object-fit: contain; margin-bottom: -5px;">
            <div style="display: flex; flex-direction: column; justify-content: flex-end; padding-bottom: 8px;">
                <p class="main-title">AIPSSS</p>
                <p class="tagline">AI Powered Student Support System</p>
                <p class="quote">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
else:
    # படம் இல்லை என்றால், வெறும் தலைப்பை மட்டும் காட்டவும்
    st.markdown('<h1 style="color:#FF4B4B; margin-top:35px;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 5. AI Core Logic (Educational Guardrails) ---
def ai_response(q, pdf_text=""):
    try:
        # 🚫 கல்வி சாரா வார்த்தைகள் கட்டுப்பாடு
        restricted = ["cinema", "movie", "actor", "actress", "song", "adult", "porn", "sexy", "violence", "kill", "suicide", "illegal", "hack", "drug", "சினிமா", "படம்", "நடிகர்", "பாடல்", "ஆபாசம்"]
        
        if any(word in q.lower() for word in restricted):
            return "மன்னிக்கவும், AIPSSS ஒரு கல்வி மற்றும் வேலைவாய்ப்பு சார்ந்த தளம் மட்டுமே. தேவையற்ற தகவல்களை என்னால் வழங்க முடியாது."

        # சிஸ்டம் விதிமுறைகள்
        system_instruction = """
        You are AIPSSS, a dedicated Educational and Career Mentor. 
        - STRICTLY answer only queries related to: Education, Competitive Exams (TNPSC, UPSC, SSC), Career Guidance, Skill Development, and Academic subjects.
        - STRICTLY refuse entertainment, movies, or illegal topics.
        - Respond in Tamil for Tamil queries and English for English queries.
        """

        # நினைவாற்றலுக்காக கடைசி 5 உரையாடல்கள்
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI & Interaction ---
# பழைய உரையாடல்களைக் காட்டுதல்
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# குரல் மற்றும் எழுத்து உள்ளீடு
voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='aipsss_mic_v3')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF கோப்புகள் மூலம் தேட", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF வெற்றிகரமாக இணைக்கப்பட்டது!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
            reply = ai_response(prompt, pdf_context)
            st.markdown(reply)
            
            # ஆடியோ பதில்
            try:
                is_tamil = bool(re.search(r'[\u0b80-\u0bff]', reply))
                tts = gTTS(text=reply[:300], lang='ta' if is_tamil else 'en')
                tts.save("response.mp3")
                st.audio("response.mp3", autoplay=True)
            except:
                pass
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
