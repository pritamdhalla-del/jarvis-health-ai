import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="JARVIS AI",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background-color:#050816;
    color:white;
}

h1 {
    text-align:center;
    color:#00f7ff;
    text-shadow:0 0 20px #00f7ff;
}

.stButton button {
    width:100%;
    background:#00f7ff;
    color:black;
    height:50px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1>JARVIS AI AGENT</h1>", unsafe_allow_html=True)

user_input = st.text_input("Command JARVIS")

if st.button("EXECUTE"):

    result = run_agent(user_input)

    st.success(result)

    # Download DOCX
    if "song_summary.docx" in result:

        with open("song_summary.docx", "rb") as file:

            st.download_button(
                label="Download Song Summary",
                data=file,
                file_name="song_summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )