#page login.py

import streamlit as st
import time

# Przykładowa baza użytkowników
users = {
    "admin": "1234",
    "robert": "1234",
    "test": "1234"
}

def show_page():
    st.title(":notes: Song2me")
    st.header(":key: Logowanie")
    username = st.text_input("Nazwa użytkownika")
    password = st.text_input("Hasło", type="password")

    if st.button("Zaloguj"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Witaj, {username}!")
            time.sleep(3)  # Opóźnienie o 3 sekundy
            st.rerun()
        else:
            st.error("Niepoprawna nazwa użytkownika lub hasło")