# page_addnew.py

import streamlit as st
from pathlib import Path

# Ścieżka do wyników

def show_page():

    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    PATH_UPLOAD.mkdir(parents=True, exist_ok=True)

    path_mp3 = PATH_UPLOAD / "new.mp3"

    st.title(":musical_score: Dodajmy nowy utwór")
    st.write("Tutaj możesz dodać nowe pliki audio.")

    if st.session_state.uploaded_mp3 is None:
        # Wczytywanie pliku MP3 
        uploaded_file = st.file_uploader("Załaduj plik MP3", type=["mp3"])
        if uploaded_file is not None:
            with open(path_mp3, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Plik zapisany jako {path_mp3}")           
            st.audio(str(path_mp3))
            if st.button("Przejdź do separacji ścieżek",use_container_width=True):
                st.session_state.uploaded_mp3 = str(path_mp3)
                st.session_state.current_menu = "page_sep"
                st.rerun()
    else:
        if (path_mp3.exists()) and (path_mp3.is_file()):
            st.write(f"Plik został już wczytany")
            st.audio(st.session_state.uploaded_mp3) 

            if st.button("Wczytaj nowy",use_container_width=True):
                st.session_state.uploaded_mp3 = None
                st.session_state.new = True
                st.session_state.current_menu = "page_addnew"
                st.rerun()
            if st.button("Przejdź do separacji ścieżek",use_container_width=True):
                st.session_state.current_menu = "page_sep"
                st.rerun()
        else:
            st.error(f"Brak pliku: {path_mp3}")
            if st.button("Wczytaj nowy",use_container_width=True):
                st.session_state.uploaded_mp3 = None
                st.session_state.new = True
                st.session_state.current_menu = "page_addnew"
                st.rerun()