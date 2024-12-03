# menu.py

import streamlit as st

def show_menu():
    # Sidebar z przyciskami
    with st.sidebar:
        st.title(":notes: Song2me")
        st.write("Użytkownik:")
        c0, c1 = st.columns([8,2])
        with c0:
            st.header(f":man-frowning: {st.session_state.username}", help="Aktualny użytkownik")
        with c1:
            if st.button(":unlock:", help="Wyloguj"):
                st.session_state.username = None
                st.session_state.logged_in = False
                st.session_state.current_menu = None
                st.rerun()

        st.write("---")
        st.header("Menu")
        if st.button("Strona główna",use_container_width=True):
            st.session_state.current_menu = None
        if st.button("Wyszukiwanie utworu",use_container_width=True):
            st.session_state.current_menu = "page_find"
        if st.button("Dodaj utwór",use_container_width=True):
            st.session_state.current_menu = "page_addnew"
        # if st.session_state.uploaded_mp3 is None:
        #     st.button("Separacja ścieżek",use_container_width=True, disabled=True)
        #     st.button("Miksowanie audio",use_container_width=True, disabled=True)    
        # else:
        if st.button("Separacja ścieżek",use_container_width=True, disabled=st.session_state.get("uploaded_mp3") is None):
            st.session_state.current_menu = "page_sep"
        if st.button("Miksowanie audio",use_container_width=True, disabled=st.session_state.get("uploaded_mp3") is None):
            st.session_state.current_menu = "page_mix"       
        if st.button("Info",use_container_width=True):
            st.session_state.current_menu = "page_info"
