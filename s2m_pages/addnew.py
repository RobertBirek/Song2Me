# page_addnew.py

import streamlit as st
from audiorecorder import audiorecorder
from dotenv import dotenv_values
from pydub import AudioSegment
from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
from io import BytesIO
import subprocess
import os
import requests

env = dotenv_values(".env")

if 'WEBSHARE_KEY' in st.secrets:
    env['WEBSHARE_KEY'] = st.secrets['WEBSHARE_KEY']
if 'WEBSHARE_USER' in st.secrets:
    env['WEBSHARE_USER'] = st.secrets['WEBSHARE_USER']
if 'WEBSHARE_PASS' in st.secrets:
    env['WEBSHARE_PASS'] = st.secrets['WEBSHARE_PASS']
if 'SPOTIFY_CLIENT_ID' in st.secrets:
    env['SPOTIFY_CLIENT_ID'] = st.secrets['SPOTIFY_CLIENT_ID']
if 'SPOTIFY_CLIENT_SECRET' in st.secrets:
    env['SPOTIFY_CLIENT_SECRET'] = st.secrets['SPOTIFY_CLIENT_SECRET']

# Autoryzacja
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = env['SPOTIFY_CLIENT_ID'],
    client_secret = env['SPOTIFY_CLIENT_SECRET']
))
###########################################################
# Pobranie informacji o utworze
def get_spotify_track(track_url):
    try:
        # Wyodrębnienie track_id z URL
        track_id = track_url.split("/")[-1].split("?")[0]
        
        # Pobranie danych o utworze
        track = sp.track(track_id)
        title = track['name']
        artist = track['artists'][0]['name']
        print(f"Utwór: {artist} - {title}")
        return f"{artist} - {title}"
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o utworze: {e}")
        return None

###########################################################
# Pobieranie audio z YouTube
def download_from_youtube(query, mp3, proxy):
    # os.makedirs(output_folder, exist_ok=True)  # Upewnij się, że katalog istnieje

    ydl_opts = {
        "format": "bestaudio",
        # "cookies": "cookies.txt",
        "cookiefile": "cookies.txt",
        # "cookies": "merged_cookies.txt",
        # "cookiesfrombrowser": ('firefox',),
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
        "geo_bypass": True, # Pomijanie ograniczeń regionalnych
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "proxy": proxy,
        # "proxy": "socks4://217.145.199.47:56746",
        "outtmpl": str(mp3),

    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch:{query}"])
    except Exception as e:
        print(f"Błąd podczas pobierania '{query}': {e}")

###########################################################
# Funkcja do pobrania muzyki za pomocą spotDL
def download_spotify_link(link, mp3):

    # Polecenie do uruchomienia spotDL
    command = [
        "spotdl",
        "--cookie-file", "cookies.txt",
        "--output", mp3 ,
        link
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return "Pobieranie zakończone sukcesem!"
    else:
        return f"Błąd podczas pobierania: {result.stderr}"

###########################################################
def show_page():

    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    PATH_UPLOAD.mkdir(parents=True, exist_ok=True)

    path_mp3 = PATH_UPLOAD / "new.mp3"

    st.title(":musical_score: Dodajmy nowy utwór")
    st.write("Tutaj możesz dodać nowe pliki audio.")

    if st.session_state.uploaded_mp3 is None:
        add_mp3, add_record,add_youtube,add_spotify = st.tabs([":musical_note: Załaduj plik", ":microphone: Nagraj mikrofonem", "Dodaj z YouTub'a", "Dodaj z Spotify"])

##########
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
##########

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
##########
        with add_youtube:
            st.subheader("Pobierz Muzykę z YouTub'a")
            # Pole do wprowadzenia linku do YouTube
            youtube_url = st.text_input("Podaj link do YouTube")

            if youtube_url:
                try:
                    # Wprowadź swój klucz API
                    # api_key = env['WEBSHARE_KEY']
                    username = env['WEBSHARE_USER']
                    password = env['WEBSHARE_PASS']
                    # api_client = ApiClient(api_key)
                    # proxies = api_client.get_proxy_list()
                    # selected_proxy = proxies.get_results[0]
                    # proxy_url = f"http://{selected_proxy.username}:{selected_proxy.password}@{selected_proxy.proxy_address}:{selected_proxy.port}"
                    
                    proxy_url = f"http://{username}:{password}@173.211.0.148:6641"
                    # Pobieranie wideo z YouTube
                    # st.write(proxy_url)
                    with st.spinner("Pobieranie wideo z YouTube..."):
                        ydl_opts = {
                            "format": "bestaudio",
                            # "cookies": "cookies.txt",
                            "cookiefile": "cookies.txt",
                            # "cookies": "merged_cookies.txt",
                            # "cookiesfrombrowser": ('firefox',),
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
                            "geo_bypass": True, # Pomijanie ograniczeń regionalnych
                            "headers": {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                "Accept-Language": "en-US,en;q=0.9",
                            },
                            # "proxy": proxy_url,
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
##########
        with add_spotify:
            st.subheader("Pobierz Muzykę ze Spotify")
            username = env['WEBSHARE_USER']
            password = env['WEBSHARE_PASS']
            proxy_url = f"http://{username}:{password}@173.0.9.70:5653"
            # Wprowadzenie linku Spotify
            spotify_link = st.text_input("Wklej link do utworu, albumu lub playlisty Spotify:")
            
            query = get_spotify_track(spotify_link)

            if query:
                print("Rozpoczynam pobieranie...")
                download_from_youtube(query, str(path_mp3),proxy_url)
                print("Proces pobierania zakończony.")
            else:
                st.error("Nie znaleziono utworów do pobrania.")



##########
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