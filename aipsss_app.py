import streamlit as st
import base64
import os

st.set_page_config(page_title="AI Smart Mentor", layout="centered")

# CSS - மிக எளிமையாக
st.markdown("""
    <style>
    .main-title { font-size: 50px !important; font-weight: 900; color: #FF4B4B; text-transform: uppercase; margin: 0; line-height: 0.8; }
    .main-tagline { color: white !important; font-style: italic; margin-top: 5px; }
    .dev-text { color: #FFD700 !important; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# லோகோ மற்றும் பெயர்கள்
st.markdown(f'''
    <div style="display: flex; align-items: center; gap: 30px;">
        <div style="font-size: 100px;">🤖</div> <div>
            <p class="main-title">AI SMART MENTOR</p>
            <p class="main-tagline">"Everyone has the right to education"</p>
            <p class="dev-text">Developed by Brammadevan</p>
        </div>
    </div>
''', unsafe_allow_html=True)
