# page_addnew.py

import streamlit as st
from audiorecorder import audiorecorder
from pydub import AudioSegment
from yt_dlp import YoutubeDL
from pathlib import Path
from io import BytesIO

# Ścieżka do wyników

def show_page():

    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    PATH_UPLOAD.mkdir(parents=True, exist_ok=True)

    path_mp3 = PATH_UPLOAD / "new.mp3"

    st.title(":musical_score: Dodajmy nowy utwór")
    st.write("Tutaj możesz dodać nowe pliki audio.")

    if st.session_state.uploaded_mp3 is None:
        add_mp3, add_record,add_youtube = st.tabs([":musical_note: Załaduj plik", ":microphone: Nagraj mikrofonem", "Dodaj z YouTub'a"])
        with add_mp3:
            # Wczytywanie pliku MP3 
            st.subheader(":musical_note: Załaduj plik Audio")
            uploaded_file = st.file_uploader("pliki audio - wideo", type=["mp3", "wav", "ogg", "mp4", "m4a", "mov", "avi"])
##
            if uploaded_file is not None:
                try:
                    # Wczytanie pliku jako BytesIO
                    file_bytes = BytesIO(uploaded_file.read())

                    # Konwersja pliku do formatu MP3 za pomocą pydub
                    with st.spinner("Konwertowanie pliku do formatu MP3..."):
                        #audio = AudioSegment.from_file(file_bytes, format=uploaded_file.type.split("/")[-1])
                        audio = AudioSegment.from_file(file_bytes)
                        mp3_buffer = BytesIO()
                        audio.export(mp3_buffer, format="mp3", bitrate="128k")
                    
                    # Zapis do pliku lokalnego
                    with open(path_mp3, "wb") as f:
                        f.write(mp3_buffer.getvalue())
                    st.success("Plik został zapisany jako 'new.mp3'.")

                except Exception as e:
                    st.error(f"Wystąpił błąd podczas konwersji: {e}")
##

        with add_record:
            st.subheader(":microphone: Nagraj swoim mikrofonem")
            rec_audio = audiorecorder(
                start_prompt="Nagraj Utwór",
                stop_prompt="Zatrzymaj nagrywanie",
            )
            if rec_audio:
                # Tworzenie obiektu BytesIO do przechowywania nagrania
                audio = BytesIO()
                rec_audio.export(audio, format="mp3")  # Eksport do formatu MP3
                rec_audio_bytes = audio.getvalue()  # Pobranie danych binarnych
                # Zapisanie pliku MP3 na dysk jako "new.mp3"
                with open(path_mp3, "wb") as f:
                    f.write(rec_audio_bytes)
                st.success(f"Nagranie zapisano jako {path_mp3}")

        with add_youtube:
            st.subheader("Załaduj z YouTub'a")
            # Pole do wprowadzenia linku do YouTube
            youtube_url = st.text_input("Podaj link do YouTube")

            if youtube_url:
                try:
                    # Pobieranie wideo z YouTube
                    with st.spinner("Pobieranie wideo z YouTube..."):
                        ydl_opts = {
                            "format": "bestaudio",
                            # "verbose": True,
                            # "noprogress": True,
                            # "force_generic_extractor": True,
                            # "postprocessors": [
                            #     {
                            #         "key": "FFmpegExtractAudio",
                            #         "preferredcodec": "mp3",
                            #         "preferredquality": "128",
                            #     }
                            # ],
                            # "geo_bypass": True, # Pomijanie ograniczeń regionalnych
                            # "headers": {
                            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            #     "Accept-Language": "en-US,en;q=0.9",
                            # },
                            "outtmpl": str(path_mp3),

                        }
                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([youtube_url])
                    # st.success(f"Pobrano plik: {audio_file}")

                    # Konwersja audio na MP3
                    with st.spinner("Konwertowanie pliku do formatu MP3..."):
                        audio = AudioSegment.from_file(path_mp3)
                        mp3_buffer = BytesIO()
                        audio.export(mp3_buffer, format="mp3", bitrate="128k")  # Konwersja do MP3 z bitrate 320 kbps

                    # Zapis pliku MP3 na dysku
                    with open(path_mp3, "wb") as f:
                        f.write(mp3_buffer.getvalue())
                    st.success("Plik został zapisany jako 'new.mp3'.")

                except Exception as e:
                    # st.write("")
                    st.error(f"Wystąpił błąd: {e}")

        if (path_mp3.exists()) and (path_mp3.is_file()): #uploaded_file or rec_audio or youtube_url:
            st.audio(str(path_mp3))
            if st.button("Przejdź do separacji ścieżek",use_container_width=True):
                st.session_state.uploaded_mp3 = str(path_mp3)
                st.session_state.current_menu = "page_sep"
                # st.rerun()
                        
    else:
        if (path_mp3.exists()) and (path_mp3.is_file()):
            st.subheader("Plik został już wczytany")
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