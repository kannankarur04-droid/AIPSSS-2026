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
    .stChatMessage { border-radius: 15px; }
    .stButton > button { height: 75px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 20px; }
    
    /* Title Styles */
    .title-text { font-size: 65px; font-weight: 900; color: #FF4B4B; margin: 0; line-height: 0.9; }
    .gold-text { color: #FFD700; font-weight: bold; margin: 0; line-height: 1.2; padding-top: 5px; }
    .quote-text { color: #FFD700; font-style: italic; margin: 0; line-height: 1.2; padding-top: 3px; font-size: 16px; }
    .white-text { color: #FFFFFF; font-size: 14px; margin: 0; line-height: 1.2; padding-top: 5px; opacity: 0.9; }
    
    /* Responsive adjustment for Mobile */
    @media (max-width: 600px) {
        .title-text { font-size: 45px; }
        .gold-text { font-size: 14px; }
        .quote-text { font-size: 13px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic (Enlarged Logo & Precise Alignment) ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    # லோகோ 220px ஆக பெரிதாக்கப்பட்டுள்ளது. 
    # flex-end அலைன்மென்ட் மூலம் பெயர்கள் லோகோவின் பாதம் அருகில் அமையும்.
    header_html = f'''
        <div style="display: flex; align-items: flex-end; gap: 25px; margin-top: 40px; margin-bottom: 35px;">
            <img src="data:image/png;base64,{base64_img}" style="width: 220px; height: auto; object-fit: contain; margin-bottom: -5px;">
            <div style="display: flex; flex-direction: column; justify-content: flex-end; padding-bottom: 8px;">
                <p class="title-text">AIPSSS</p>
                <p class="gold-text">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="white-text">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)
else:
    st.markdown('<h1 style="color:#FF4B4B;">AIPSSS</h1>', unsafe_allow_html=True)

# --- 🧠 5. AI Logic (Strict Educational Rules) ---
def ai_response(user_query, pdf_text=""):
    try:
        restricted = ["cinema", "movie", "actor", "actress", "song", "adult", "porn", "sexy", "violence", "kill", "suicide", "illegal", "hack", "drug", "சினிமா", "படம்", "நடிகர்", "பாடல்", "ஆபாசம்", "கொலை", "தற்கொலை"]
        if any(word in user_query.lower() for word in restricted):
            return "மன்னிக்கவும், AIPSSS ஒரு கல்வி மற்றும் வேலைவாய்ப்பு சார்ந்த தளம் மட்டுமே. கல்வி சாரா அல்லது தேவையற்ற தகவல்களை என்னால் வழங்க முடியாது."

        system_instruction = "You are AIPSSS, a dedicated Educational Mentor. Only help with studies and career."
        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1200]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச இங்கே அழுத்தவும்", stop_prompt="🛑 நிறுத்த அழுத்தவும்", language='ta-IN', use_container_width=True, key='mic_aipsss_v3')
text_input = st.chat_input("கேள்வியைத் தட்டச்சு செய்யவும்...")
uploaded_pdf = st.file_uploader("📂 PDF மூலம் தேட", type=["pdf"])

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
        with st.spinner("ஆராய்கிறேன்..."):
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
