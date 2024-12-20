# separate.py

import streamlit as st
from dotenv import dotenv_values
from pathlib import Path
import subprocess
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import requests
import base64
import json

env = dotenv_values(".env")

if 'ACR_ACCESS_KEY' in st.secrets:
    env['ACR_ACCESS_KEY'] = st.secrets['ACR_ACCESS_KEY']
if 'ACR_SECRET_KEY' in st.secrets:
    env['ACR_SECRET_KEY'] = st.secrets['ACR_SECRET_KEY']


######################################################################

######################################################################
def is_quiet(file_path, threshold_db=-40):
    audio = AudioSegment.from_file(file_path)
    avg_dbfs = audio.dBFS  # Obliczanie średniego poziomu głośności w dBFS
    max_dbfs = audio.max_dBFS

    print(f"Średnia głośność pliku: {avg_dbfs:.2f} dBFS  Max: {max_dbfs:.2f} dBFS")
    return avg_dbfs < threshold_db
######################################################################
def separate_mp3():
    # Ścieżka do wyników
    PATH_SEPARATE = Path("users") / st.session_state.username / "songs" /"new"
    PATH_SEPARATE.mkdir(parents=True, exist_ok=True)

    new_mp3_dir = st.session_state.uploaded_mp3
 
    # st.write(f"plik: {new_mp3_dir}")
    # st.write(f"separuje do {str(PATH_SEPARATE)}")
    with st.spinner("Separuje ścieżki. Chwilę to potrwa. Możesz posłuchać utworu."):
        result = subprocess.run(
            # ["demucs", "-n", "htdemucs", new_mp3_dir, "--out", str(PATH_SEPARATE), "--mp3"],
            ["demucs", "-n", "htdemucs_6s", new_mp3_dir, "--out", str(PATH_SEPARATE), "--filename", "{stem}.{ext}", "--mp3", "--mp3-bitrate", "128", "--mp3-preset", "2"],   #htdemucs_6s
            # ["demucs", "-n", "htdemucs", new_mp3_dir, "--out", str(PATH_SEPARATE), "--filename", "{stem}.{ext}", "--mp3", "--mp3-bitrate", "128", "--mp3-preset", "7"],   #htdemucs_6s
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        st.success("Separacja zakończona!")

        # Ścieżki wynikowe
        vocal_path = PATH_SEPARATE / "htdemucs_6s" / "vocals.mp3"
        st.session_state.vocal_path = str(vocal_path)
        drums_path = PATH_SEPARATE / "htdemucs_6s" / "drums.mp3"
        st.session_state.drums_path = str(drums_path)
        bass_path = PATH_SEPARATE / "htdemucs_6s" / "bass.mp3"
        st.session_state.bass_path = str(bass_path)
        guitar_path = PATH_SEPARATE / "htdemucs_6s" / "guitar.mp3"
        st.session_state.guitar_path = str(guitar_path)
        piano_path = PATH_SEPARATE / "htdemucs_6s" / "piano.mp3"
        st.session_state.piano_path = str(piano_path)
        other_path = PATH_SEPARATE / "htdemucs_6s" / "other.mp3"
        st.session_state.other_path = str(other_path)

        # Odtwarzanie wyników
        list_separated()

    else:
        st.error("Wystąpił błąd podczas separacji.")
        st.text(result.stderr)

######################################################################
def list_separated():

    PATH_SEPARATE = Path("users") / st.session_state.username / "songs" / "new" / "htdemucs_6s"
    vocal_path = PATH_SEPARATE / "vocals.mp3"
    drums_path = PATH_SEPARATE / "drums.mp3"
    bass_path = PATH_SEPARATE / "bass.mp3"
    guitar_path = PATH_SEPARATE / "guitar.mp3"
    piano_path = PATH_SEPARATE / "piano.mp3"
    other_path = PATH_SEPARATE / "other.mp3"

    ok = False
    
    if vocal_path.exists() and vocal_path.is_file():
        st.write("---")
        st.subheader("Utwór został podzielony na ścieżki")
        st.write("---")
        ok = True
        st.write(":microphone: wokal")
        st.audio(str(vocal_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(vocal_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz wokal MP3",
                    data=file_data,
                    file_name="vocals.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(vocal_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k0"):
                    st.write("usunięto")
    
    if drums_path.exists() and drums_path.is_file():
        st.write("---")
        ok = True
        st.write(":long_drum: perkusja")
        st.audio(str(drums_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(drums_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz perkusje MP3",
                    data=file_data,
                    file_name="drums.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(drums_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k1"):
                    st.write("usunięto")    
    
    if bass_path.exists() and bass_path.is_file():
        st.write("---")
        ok = True
        st.write(":violin: bass")
        st.audio(str(bass_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(bass_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz bass MP3",
                    data=file_data,
                    file_name="bass.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(bass_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k2"):
                    st.write("usunięto")  
    
    if guitar_path.exists() and guitar_path.is_file():
        st.write("---")
        ok = True
        st.write(":guitar: gitara")
        st.audio(str(guitar_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(guitar_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz gitara MP3",
                    data=file_data,
                    file_name="guitar.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(guitar_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k3"):
                    st.write("usunięto")  
    
    if piano_path.exists() and piano_path.is_file():
        st.write("---")
        ok = True
        st.write(":musical_keyboard: piano")
        st.audio(str(piano_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(piano_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz piano MP3",
                    data=file_data,
                    file_name="piano.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(piano_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k4"):
                    st.write("usunięto")  
    
    if other_path.exists() and other_path.is_file():
        st.write("---")
        ok = True
        st.write(":notes: pozostałe")
        st.audio(str(other_path), format="audio/mp3")
        c0, c1 = st.columns(2)
        with c0:
            with open(str(other_path), "rb") as file:
                file_data = file.read()
                st.download_button(
                    label="Pobierz other MP3",
                    data=file_data,
                    file_name="other.mp3",
                    mime="audio/mpeg"
                )
        with c1:
            if is_quiet(str(other_path)):
                if st.button("Plik pusty - Usuń",use_container_width=True, key="k5"):
                    st.write("usunięto")  

    return ok

######################################################################

def show_page():
    st.title(":musical_score: Separacja ścieżek")
    st.write("Oddziel wokale i instrumenty w plikach audio.")

    path_mp3 = Path(st.session_state.uploaded_mp3)

    song = ""
    if st.session_state['mp3_info']['title'] is not "":
        song =str(f"{st.session_state['mp3_info']['artist']} - {st.session_state['mp3_info']['title']}")

    if st.session_state.uploaded_mp3 is not None:
        if (path_mp3.exists()) and (path_mp3.is_file()):
            st.subheader(f"Utwór został wczytany: {song}")
            st.audio(st.session_state.uploaded_mp3, format="audio/mp3")            
            c0, c1 = st.columns(2)
            with c0:
                with open(st.session_state.uploaded_mp3, "rb") as file:
                    file_data = file.read()
                    st.download_button(
                        label="Pobierz MP3",
                        data=file_data,
                        file_name="new.mp3",
                        mime="audio/mpeg"
                    )
            with c1:
                if st.button("Wczytaj nowy",use_container_width=True):
                    st.session_state.uploaded_mp3 = None
                    st.session_state.new = True
                    st.session_state.current_menu = "page_addnew"
                    st.rerun()

            # list_separated()
            if not list_separated():
                st.write("---")
                if st.button("Separuj ścieżki",use_container_width=True, key="s1"):
                    separate_mp3()
        else:
            st.error(f"Brak pliku: {path_mp3}")
            if st.button("Wczytaj nowy",use_container_width=True, key="n1"):
                st.session_state.uploaded_mp3 = None
                st.session_state.current_menu = "page_addnew"
                st.rerun()
    else:
        st.error(f"Brak pliku: {path_mp3}")
        if st.button("Wczytaj nowy",use_container_width=True, key="n2"):
            st.session_state.uploaded_mp3 = None
            st.session_state.current_menu = "page_addnew"
            st.rerun()