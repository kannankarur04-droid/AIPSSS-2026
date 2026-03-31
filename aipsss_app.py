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

# --- 🎨 2. Styling (CSS) - Responsive & Aligned ---
st.set_page_config(page_title="AIPSSS", layout="centered", page_icon="🤖🎓")

st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    
    .aipsss-header {
        display: flex;
        align-items: center; 
        justify-content: flex-start;
        gap: 10px;
        margin-bottom: 25px;
        margin-top: 10px;
        width: 100%;
    }

    .content-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: left;
    }

    /* Desktop View */
    @media (min-width: 769px) {
        .main-logo { width: 180px; height: auto; }
        .main-title { font-size: 4.5rem !important; line-height: 0.8 !important; }
        .subtitle { font-size: 1.5rem !important; }
        .quote-text { font-size: 1.1rem !important; }
        .developer { font-size: 1rem !important; }
    }

    /* Mobile View - Fixed Alignment */
    @media (max-width: 768px) {
        .aipsss-header { gap: 8px; flex-wrap: nowrap; }
        .main-logo { width: 95px !important; height: auto; }
        .main-title { font-size: 2.2rem !important; line-height: 0.9 !important; }
        .subtitle { font-size: 0.8rem !important; line-height: 1.1 !important; }
        .quote-text { font-size: 0.75rem !important; line-height: 1.1 !important; }
        .developer { font-size: 0.65rem !important; }
    }

    .main-title { font-weight: 900 !important; color: #ff4d4d !important; margin: 0 !important; }
    .subtitle { color: #FFD700 !important; margin: 0 !important; font-weight: bold !important; }
    .quote-text { font-style: italic !important; color: #FFD700 !important; margin: 0 !important; }
    .developer { color: #FFFFFF !important; opacity: 0.8 !important; margin: 0 !important; }

    .stButton > button { height: 65px !important; width: 100% !important; border-radius: 15px !important; background-color: #FF4B4B !important; color: white !important; font-weight: bold; font-size: 18px; }
    .stChatMessage { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 🧠 3. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 🖼️ 4. Header Logic ---
img_name = 'aipsss_robot_final.png' 
img_path = os.path.join(os.getcwd(), img_name)

def get_base64_image(image_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

base64_img = get_base64_image(img_path)

if base64_img:
    header_html = f'''
        <div class="aipsss-header">
            <img src="data:image/png;base64,{base64_img}" alt="AIPSSS Logo" class="main-logo">
            <div class="content-box">
                <h1 class="main-title">AIPSSS</h1>
                <p class="subtitle">AI Powered Student Support System</p>
                <p class="quote-text">"Everyone has the right to education"</p>
                <p class="developer">Developed by Kannan</p>
            </div>
        </div>
    '''
    st.markdown(header_html, unsafe_allow_html=True)

# --- 🧠 5. AI Engine (The Pure Educational Filter) ---
def ai_response(user_query, pdf_text=""):
    try:
        # 🚫 நேரடித் தடை பட்டியல் (Gaming, Illegal, Cinema)
        forbidden = [
            "game", "gaming", "play", "pubg", "free fire", "cheat", "hack", "illegal", "movie", "song", "actor",
            "விளையாட்டு", "கேம்", "சினிமா", "படம்", "நடிகர்", "பாடல்", "ஹேக்", "சண்டை"
        ]
        
        # ⚠️ வார்த்தை அடிப்படையில் தடுப்பு
        if any(word in user_query.lower() for word in forbidden):
            return "மன்னிக்கவும் கண்ணன், நான் ஒரு கல்வி உதவியாளர் (Educational Assistant). படிப்பு, வேலைவாய்ப்பு மற்றும் போட்டித் தேர்வுகள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதில் அளிக்க முடியும். விளையாட்டு அல்லது பொழுதுபோக்கு தொடர்பான தகவல்களை நான் வழங்கமாட்டேன்."

        # 🧠 சிஸ்டம் கட்டளைகள் - இன்னும் கடுமையாக
        system_instruction = """
        STRICT RULES FOR AIPSSS:
        1. YOU ARE AN EDUCATION-ONLY ASSISTANT.
        2. STRICTLY REFUSE: Gaming, Movies, Sports (unless academic), Music, Adult content, or Illegal acts.
        3. IF A USER ASKS ABOUT GAMES: Politley state that you only help with Education and Careers. 
        4. NEVER PROVIDE INSTRUCTIONS FOR PLAYING GAMES.
        5. Tone: Helpful mentor. No long moral lectures.
        6. Response Language: Tamil for Tamil, English for English.
        """

        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]]
        context = f"PDF Context: {pdf_text[:1000]}\n" if pdf_text else ""
        messages = [{"role": "system", "content": system_instruction}] + history + [{"role": "user", "content": context + user_query}]

        # Temperature 0.1 - இது AI-ஐ விதிகளை விட்டு விலகாமல் வைத்திருக்கும்
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0.1)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 🎙️ 6. UI Interaction ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_input = speech_to_text(start_prompt="🎤 பேச அழுத்தவும்", stop_prompt="🛑 நிறுத்த", language='ta-IN', use_container_width=True, key='mic_final_v21')
text_input = st.chat_input("கல்வி தொடர்பான கேள்வியைக் கேட்கவும்...")
uploaded_pdf = st.file_uploader("📂 கல்வி சார்ந்த PDF கோப்புகள்", type=["pdf"])

pdf_context = ""
if uploaded_pdf:
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    pdf_context = "".join([page.get_text() for page in doc])
    st.success("✅ PDF கோப்பு இணைக்கப்பட்டது!")

prompt = voice_input if voice_input else text_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("சிந்திக்கிறேன்..."):
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
