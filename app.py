import streamlit as st
from pathlib import Path
import subprocess
import numpy as np
#from pydub import AudioSegment
from s2m_pages import menu, main, info, find, addnew, separate, mix, login

######################################################

st.set_page_config(page_title="Song2me",page_icon=":notes:")

######################################################
def load_mp3(user):
    PATH_UPLOAD = Path("users") / user / "songs" / "new" / "new.mp3"
    PATH_SEPARATE = Path("users") / user / "songs" / "new" / "htdemucs_6s"
    vocal_path = PATH_SEPARATE / "vocals.mp3"
    drums_path = PATH_SEPARATE / "drums.mp3"
    bass_path = PATH_SEPARATE / "bass.mp3"
    guitar_path = PATH_SEPARATE / "guitar.mp3"
    piano_path = PATH_SEPARATE / "piano.mp3"
    other_path = PATH_SEPARATE / "other.mp3"

    if PATH_UPLOAD.exists() and PATH_UPLOAD.is_file():
        st.session_state.uploaded_mp3 = str(PATH_UPLOAD)
    
    if vocal_path.exists() and vocal_path.is_file():
        st.session_state.vocal_path = str(vocal_path)
    if drums_path.exists() and drums_path.is_file():
        st.session_state.drums_path = str(drums_path)
    if bass_path.exists() and bass_path.is_file():
        st.session_state.bass_path = str(bass_path)
    if guitar_path.exists() and guitar_path.is_file():
        st.session_state.guitar_path = str(guitar_path)
    if piano_path.exists() and piano_path.is_file():
        st.session_state.piano_path = str(piano_path)
    if other_path.exists() and other_path.is_file():
        st.session_state.other_path = str(other_path)

######################################################
# Inicjalizacja session_state, jeśli nie istnieje
if "current_menu" not in st.session_state:
    st.session_state.current_menu = None
if "uploaded_mp3" not in st.session_state:
    st.session_state.uploaded_mp3 = None
if "vocal_path" not in st.session_state:
    st.session_state.vocal_path = None
if "drums_path" not in st.session_state:
    st.session_state.drums_path = None
if "bass_path" not in st.session_state:
    st.session_state.bass_path = None
if "other_path" not in st.session_state:
    st.session_state.other_path = None
if "username" not in st.session_state:
    st.session_state.username = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
######################################################

if (st.session_state.username is not None) and (st.session_state.logged_in == True):
    load_mp3(st.session_state.username)  # jeżeli jest niedokończona piosenka

# Logowanie
if not st.session_state.logged_in:
    login.show_page()
else:
    # Wywołanie menu
    menu.show_menu()

    # Wyświetlanie treści w zależności od wybranego menu
    if st.session_state.current_menu == None:
        main.show_page()
    #############################################################
    elif st.session_state.current_menu == "page_find":
        find.show_page()
    #############################################################
    elif st.session_state.current_menu == "page_addnew":
        addnew.show_page()
    #############################################################
    elif st.session_state.current_menu == "page_sep":
        separate.show_page()
    #############################################################
    elif st.session_state.current_menu == "page_mix":
        mix.show_page()
    #############################################################    
    elif st.session_state.current_menu == "page_info":
        info.show_page()
    #############################################################