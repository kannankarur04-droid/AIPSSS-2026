import streamlit as st
import google.generativeai as genai

# 🔐 API Key Setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS", layout="wide", page_icon="🎓")
st.title("🎓 AI Powered Student Support System (AIPSSS)")

SYSTEM_PROMPT = "Explain concepts simply with examples. Use LaTeX for math. Add 2 MCQs at the end."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your educational doubt..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # ⚡ Streaming response
            responses = model.generate_content(SYSTEM_PROMPT + "\n\nQ: " + prompt, stream=True)
            for chunk in responses:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error: {e}") # என்ன எர்ரர் என்று துல்லியமாகத் தெரியும்
