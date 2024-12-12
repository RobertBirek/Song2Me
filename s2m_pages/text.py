# page_find.py

import streamlit as st

def show_page():
    st.title(":abcd: Rozpoznaj tekst")
    st.write("Tutaj rozpoznasz tekst piosenki.")
    
    if st.session_state['mp3_info']['title'] is not "":
        st.write("---")
        st.subheader(f"{st.session_state['mp3_info']['artist']} - {st.session_state['mp3_info']['title']}")
        st.write("---")
