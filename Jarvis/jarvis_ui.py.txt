import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import webbrowser

# Load API Key
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Page Config
st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>

body {
    background-color: #050816;
}

.main {
    background: linear-gradient(135deg, #050816, #0b1026);
    color: white;
}

h1 {
    color: #00f7ff;
    text-align: center;
    font-size: 60px;
    text-shadow: 0 0 20px #00f7ff;
}

.stTextInput > div > div > input {
    background-color: rgba(0,255,255,0.08);
    color: white;
    border: 1px solid #00f7ff;
    border-radius: 12px;
    padding: 15px;
}

.stButton button {
    width: 100%;
    background: linear-gradient(90deg,#00f7ff,#007cf0);
    color: white;
    border-radius: 12px;
    border: none;
    height: 50px;
    font-size: 18px;
    box-shadow: 0 0 20px #00f7ff;
}

.chat-box {
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(0,255,255,0.2);
    margin-top: 20px;
    box-shadow: 0 0 25px rgba(0,255,255,0.15);
}

.sidebar .sidebar-content {
    background-color: #0b1026;
}

</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>JARVIS AI</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚡ JARVIS CONTROL")

st.sidebar.markdown("""
### Features
- AI Chat
- Chrome Launcher
- YouTube Search
- Google Search
- Automation
- Localhost AI
""")

# Input
user_input = st.text_input("Command JARVIS")

# Button
if st.button("EXECUTE COMMAND"):

    # Open Chrome
    if "open chrome" in user_input.lower():
        os.system("start chrome")
        st.success("Opening Chrome...")

    # YouTube
    elif "youtube" in user_input.lower():

        query = user_input.lower()
        query = query.replace("play", "")
        query = query.replace("on youtube", "")
        query = query.replace("youtube", "")
        query = query.strip()

        url = f"https://www.youtube.com/results?search_query={query}"

        webbrowser.open(url)

        st.success(f"Playing {query} on YouTube")

    # Google
    elif "google" in user_input.lower():

        query = user_input.lower()
        query = query.replace("search google for", "")
        query = query.strip()

        url = f"https://www.google.com/search?q={query}"

        webbrowser.open(url)

        st.success(f"Searching Google for {query}")

    # AI CHAT
    else:

        with st.spinner("JARVIS THINKING..."):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )

            answer = response.choices[0].message.content

            st.markdown(f'''
            <div class="chat-box">
            <h3>🤖 JARVIS RESPONSE</h3>
            <p>{answer}</p>
            </div>
            ''', unsafe_allow_html=True)