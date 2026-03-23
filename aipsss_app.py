import streamlit as st
import google.generativeai as genai

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please set GOOGLE_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="AIPSSS - Student Assistant", layout="wide", page_icon="🎓")
st.title("🎓 AI Powered Student Support System (AIPSSS)")

SYSTEM_PROMPT = """You are an expert Educational Consultant. 
Explain concepts simply with real-world examples. 
Use LaTeX for math/science formulas (e.g., $E=mc^2$). 
At the end, provide 2 Multiple Choice Questions (MCQs) for the user to test their understanding."""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your educational doubt..."):
    if len(prompt) > 200:
        st.warning("⚠️ தயவுசெய்து சுருக்கமான கேள்வியைக் கேட்கவும் (Max 200 chars).")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty() # பதிலுக்கான காலி இடம்
            full_response = ""
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                responses = model.generate_content(
                    SYSTEM_PROMPT + "\n\nQ: " + prompt,
                    stream=True
                )
                
                for chunk in responses:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error("⚠️ தற்போது சர்வர் பிஸியாக உள்ளது. மீண்டும் முயற்சிக்கவும்.")