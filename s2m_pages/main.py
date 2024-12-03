# page_main.py

import streamlit as st

def show_page():
    st.title(":notes: Strona główna")
    st.write("Witaj w aplikacji audio! Kliknij przyciski w menu, aby przejść do funkcji.")
    if st.button("Wyszukaj isniejący utwór",use_container_width=True):
        st.session_state.current_menu = "page_find"
        st.rerun()
    if st.button("Dodaj nowy utwór",use_container_width=True):
        st.session_state.current_menu = "page_addnew"
        st.rerun()