# --- 🎨 2. Styling (CSS) - 'Final Logo' Design ---
# இதிலிருந்து காப்பி செய்யவும்
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem !important; max-width: 1000px; }

    /* Custom Header Container */
    .mentor-header {
        display: flex;
        align-items: flex-end; 
        gap: 25px;
        margin-bottom: -18px; 
        padding-left: 20px;
    }

    /* Logo - Big & Stepping on Input Box */
    .header-logo {
        width: 280px !important; 
        height: auto;
        margin-bottom: -12px; 
        z-index: 10;
    }

    /* Header Text Box - நீங்கள் கொடுத்த புதிய அளவுகள் */
    .header-text {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding-bottom: 25px; 
    }

    /* AI STUDENT MENTOR - RED (நீங்கள் கொடுத்த புதிய அளவுகள்) */
    .header-text h1 {
        font-family: 'Lexend', sans-serif;
        font-size: 55px !important; 
        color: #FF4B4B !important; 
        margin: 0 !important;
        font-weight: 900 !important;
        line-height: 0.8 !important; 
        letter-spacing: -2px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* Tagline - White */
    .tagline {
        font-family: 'Lexend', sans-serif;
        font-size: 20px !important;
        color: #FFFFFF !important; 
        margin: 6px 0 0 0 !important;
        font-style: italic;
        line-height: 1.0 !important;
    }

    /* Developer - Gold */
    .developer {
        font-family: 'Lexend', sans-serif;
        font-size: 16px !important;
        color: #FFD700 !important; 
        margin: 4px 0 0 0 !important;
        font-weight: bold;
        line-height: 1.0 !important;
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Buttons */
    .stButton > button { 
        height: 60px !important; 
        border-radius: 12px !important; 
        background-color: #FF4B4B !important; 
        color: white !important; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True) # <--- இந்த வரி தான் கோடை டிசைனாக மாற்றும்

# --- 🖼️ Header Display Logic ---
if base64_img:
    st.markdown(f'''
        <header class="mentor-header">
            <img src="data:image/png;base64,{base64_img}" alt="Logo" class="header-logo">
            <div class="header-text">
                <h1>AI STUDENT MENTOR</h1>
                <p class="tagline">"Everyone has the right to education"</p>
                <p class="developer">Developed by Brammadevan</p>
            </div>
        </header>
    ''', unsafe_allow_html=True)
# இதுவரை மாற்றவும்
