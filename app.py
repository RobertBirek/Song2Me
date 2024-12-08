import streamlit as st
from audiorecorder import audiorecorder
from pathlib import Path
from dotenv import dotenv_values
import configparser
import shutil
import os
import subprocess
import requests
import numpy as np
from pydub import AudioSegment
from s2m_pages import menu, main, info, find, addnew, separate, mix, login, about, setup

######################################################

st.set_page_config(page_title="Song2me",page_icon=":notes:")

env = dotenv_values(".env")

if 'PROXY_URL' in st.secrets:
    env['PROXY_URL'] = st.secrets['PROXY_URL']

######################################################
def load_config(user):
    PATH_UPLOAD = Path("users") / user / "songs" / "new" / "new.mp3"
    PATH_SEPARATE = Path("users") / user / "songs" / "new" / "htdemucs_6s"
    USER_PATH= Path("users") / user
    CONFIG_FILE = USER_PATH / "setup.cfg"
    vocal_path = PATH_SEPARATE / "vocals.mp3"
    drums_path = PATH_SEPARATE / "drums.mp3"
    bass_path = PATH_SEPARATE / "bass.mp3"
    guitar_path = PATH_SEPARATE / "guitar.mp3"
    piano_path = PATH_SEPARATE / "piano.mp3"
    other_path = PATH_SEPARATE / "other.mp3"

    config = configparser.ConfigParser(interpolation=None)  # Wyłączenie interpolacji
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        value=config['settings'].getboolean('use_proxy')
        st.session_state.use_proxy = value

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

##############################

def delete_new_song(user):
    del_path = Path("users") / user / "songs" / "new"
    # Sprawdzenie, czy katalog istnieje
    if del_path.exists() and del_path.is_dir():
        shutil.rmtree(del_path)  # Usunięcie całego katalogu
        print(f"Katalog {del_path} został usunięty.")
        st.session_state.new = False
    else:
        print(f"Katalog {del_path} nie istnieje.")
##########    
def fetch_proxy_list():
    """
    Pobiera listę proxy z podanego URL i zwraca ją jako listę.

    Args:
        download_url (str): URL do pobrania listy proxy.

    Returns:
        list: Lista serwerów proxy (każdy jako string "ip:port:username:password").
    """
    download_url = env['PROXY_URL']
    try:
        # Pobranie listy proxy
        response = requests.get(download_url)
        response.raise_for_status()  # Sprawdzenie błędów HTTP

        # Rozdzielenie listy proxy na linie
        return response.text.strip().split("\n")
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania listy proxy: {e}")
        return []
######################################################

if "new" not in st.session_state:
    st.session_state.new = False

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
if "proxy_list" not in st.session_state:
    st.session_state["proxy_list"] = None
if "current_proxy" not in st.session_state:
    st.session_state.current_proxy = None
if "use_proxy" not in st.session_state:
    st.session_state.use_proxy = False
######################################################
if (st.session_state.new == True):
    delete_new_song(st.session_state.username)

if (st.session_state.username is not None) and (st.session_state.logged_in == True):
    load_config(st.session_state.username)  # jeżeli jest niedokończona piosenka

# Logowanie
if not st.session_state.logged_in:
    login.show_page()
else:
    if st.session_state.use_proxy:
        if "proxy_list" not in st.session_state:
            proxy_list = fetch_proxy_list()
            if proxy_list:
                st.session_state["proxy_list"] = proxy_list
                print(f"Pobrano {len(proxy_list)} serwerów proxy.")
            else:
                print("Nie udało się pobrać listy proxy.")

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
    elif st.session_state.current_menu == "page_about":
        about.show_page()
    #############################################################
    elif st.session_state.current_menu == "page_setup":
        setup.show_page()
    #############################################################