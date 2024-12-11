# page_setup.py

import streamlit as st
from pathlib import Path
import configparser
import os

# Ścieżka do pliku konfiguracji
USER_PATH = ""
CONFIG_FILE = USER_PATH / "setup.cfg"
COOKIE_FILE = USER_PATH / "cookies.txt"

############################################
def generate_cookies_file(cookies_data, output_file="cookies.txt"):
    """
    Generuje plik cookies.txt z podanych danych.
    """
    try:
        with open(output_file, "w") as f:
            f.write(cookies_data)
        st.success(f"Plik {output_file} został wygenerowany.")
    except Exception as e:
        st.error(f"Wystąpił błąd podczas generowania pliku: {e}")

def load_settings():
    """
    Ładuje ustawienia z pliku setup.cfg.
    Jeśli plik nie istnieje, zwraca wartości domyślne.
    """
    config = configparser.ConfigParser(interpolation=None)  # Wyłączenie interpolacji
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config['settings'] = {
            'use_proxy': 'false',
            'cookies': ''
        }
    return config

def save_settings(config):
    """
    Zapisuje ustawienia do pliku setup.cfg.
    """
    st.session_state.use_proxy = config['settings'].getboolean('use_proxy')
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)


def show_page():
    st.title(":hammer_and_wrench: Ustawienia")
    st.header("Ustawienia")
    # Ścieżka do pliku konfiguracji
    USER_PATH= Path("users") / str(st.session_state.username)
    CONFIG_FILE = USER_PATH / "setup.cfg"
    COOKIE_FILE = USER_PATH / "cookies.txt"

    config = load_settings()
    help = """Pobierz i zainstaluj narzędzie do eksportu plików cookie, takie jak EditThisCookie (dla Chrome) lub Cookies.txt (dla Firefox).
Zaloguj się na YouTube w przeglądarce, a następnie użyj rozszerzenia, aby wyeksportować pliki cookie jako plik cookies.txt.
Otwórz plik cookies.txt i znajdź linie zaczynające się od .youtube.com – będą zawierały dane sesji niezbędne do uwierzytelnienia."""
    use_proxy = st.checkbox("Używaj proxy", value=config['settings'].getboolean('use_proxy'))
    cookies = st.text_area(
        "Wprowadź dane cookies (w formacie Netscape HTTP Cookie File):",
        value=config['settings'].get('cookies', ''),
        help=help
    )

    if st.button("Zapisz ustawienia"):
        config['settings']['use_proxy'] = str(use_proxy).lower()
        config['settings']['cookies'] = cookies
        save_settings(config)
        st.success("Ustawienia zostały zapisane.")

    # Generowanie pliku cookies.txt
    if st.button("Generuj cookies.txt"):
        if cookies.strip():
            generate_cookies_file(cookies,COOKIE_FILE)
        else:
            st.error("Dane cookies są puste. Wprowadź dane przed generowaniem pliku.")

