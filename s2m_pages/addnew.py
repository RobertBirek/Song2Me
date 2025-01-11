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
import random
import configparser
import os

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
if 'PROXY_URL' in st.secrets:
    env['PROXY_URL'] = st.secrets['PROXY_URL']

# Autoryzacja
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = env['SPOTIFY_CLIENT_ID'],
    client_secret = env['SPOTIFY_CLIENT_SECRET']
))


path_mp3 = ""
config_mp3 = ""

###########################################################
# Pobranie informacji o utworze
def get_spotify_track(track_url):
    try:
        # Wyodrębnienie track_id z URL
        track_id = track_url.split("/")[-1].split("?")[0]
        
        # Pobranie danych o utworze
        track = sp.track(track_id)
        title = track['name']
        artist = ", ".join([artist['name'] for artist in track['artists']])
        album = track['album']['name']
        # duration_ms = track['duration_ms']
        # duration_min = duration_ms / 60000  # Konwersja na minuty
        track_number = track['track_number']
        # album_total_tracks = track['album']['total_tracks']
        release_date = track['album']['release_date']
        album_image = track['album']['images'][0]['url'] if track['album']['images'] else None

        # Zapis danych do st.session_state
        st.session_state['mp3_info'] = {
            "title": title,
            "artist": artist,
            "album": album,
            "genres": "",
            "track_number": track_number,
            "release_date": release_date,
            "album_image": album_image
        }

        # # Sprawdzenie i wyświetlenie danych utworu
        # if 'mp3_info' in st.session_state:
        #     track = st.session_state['mp3_info']
        #     st.write("Aktualny utwór:")
        #     st.text(f"{track['artist']} - {track['title']}")
        #     st.text(f"Album: {track['album']} ({track['release_date']})")
        #     if track['album_image']:
        #         st.image(track['album_image'], caption="Okładka albumu")
        
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(config_mp3):
            config.read(config_mp3)

        print(f"Utwór: {artist} - {title} z Albumu {album} - {release_date}" )
        return f"{artist} - {title} {album} {release_date}"
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o utworze: {e}")
        return None

###########################################################

################
def get_random_proxy_from_state():
    """
    Losowo wybiera jeden serwer proxy z zapisanej listy w session_state.

    Returns:
        dict: Losowy serwer proxy w formie słownika (IP, port, username, password).
    """
    if "proxy_list" in st.session_state and st.session_state["proxy_list"]:
        random_proxy = random.choice(st.session_state["proxy_list"])
        parts = random_proxy.split(":")
        
        ip = parts[0]
        port = parts[1]
        username = parts[2] if len(parts) > 2 else None
        password = parts[3] if len(parts) > 3 else None

        proxy_url = f"http://{username}:{password}@{ip}:{port}"
        
        return proxy_url     
        # return {
        #     "ip": parts[0],
        #     "port": parts[1],
        #     "username": parts[2] if len(parts) > 2 else None,
        #     "password": parts[3] if len(parts) > 3 else None,
        # }
    return None

###########################################################
# Pobieranie audio z YouTube
def download_from_youtube(url, query, out_path):
    # os.makedirs(output_folder, exist_ok=True)  # Upewnij się, że katalog istnieje
    
    USER_PATH= Path("users") / str(st.session_state.username)
    COOKIE_FILE = USER_PATH / "cookies.txt"
    if COOKIE_FILE.exists() and COOKIE_FILE.is_file():
        cookies = str(COOKIE_FILE)
    
    # proxies = st.session_state["proxy_list"]
    # st.write(proxies[0])
    # current_proxy_index = 0
    # # proxy = st.session_state.current_proxy

    success = False
 
    while not success:
        proxy = get_random_proxy_from_state()
        st.session_state.current_proxy = proxy

        ydl_opts = {
            "format": "bestaudio", #"bestaudio/best",
            "cookiefile": cookies, #"cookies.txt",
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
            "outtmpl": str(out_path),
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                if url is not None:
                    ydl.download([url])
                else:
                    if query is not None:
                        ydl.download([f"ytsearch:{query}"])
            success = True
                
        except Exception as e:
            print(f"Błąd podczas pobierania '{query}': {e}")
            success = False

    if not success:
        print("Nie udało się pobrać pliku. Wszystkie proxy zostały wypróbowane.")
        st.error("Nie udało się pobrać pliku. Wszystkie proxy zostały wypróbowane.")
###########################################################
def show_page():

    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    PATH_UPLOAD.mkdir(parents=True, exist_ok=True)
    path_mp3 = PATH_UPLOAD / "new.mp3"
    config_mp3 = PATH_UPLOAD / "new.cfg"
    
    st.session_state['mp3_info'] = {
        "title": "",
        "artist": "",
        "album": "",
        "genres": "",
        "track_number": "",
        "release_date": "",
        "album_image": ""
    }
    path_mp3 = PATH_UPLOAD / "new.mp3"

    st.title(":musical_score: Dodajmy nowy utwór")
    st.write("Tutaj możesz dodać nowe pliki audio.")
 ######proxy
    if st.session_state.use_proxy:
        if "proxy_list" in st.session_state:
            proxy = get_random_proxy_from_state()
            if proxy:
                st.session_state.current_proxy = proxy
                print(f"Wybrano serwer proxy: {proxy}")
            else:
                print("Nie udało się wybrać serwera proxy.")
        else:
            print("Lista proxy nie została jeszcze pobrana.")    
        
        st.write(f"Aktualne proxy: {st.session_state.current_proxy}")
 ######proxy
 #    
    if st.session_state.uploaded_mp3 is None:
        add_mp3, add_record,add_youtube,add_spotify = st.tabs([":musical_note: Załaduj plik", ":microphone: Nagraj mikrofonem", "Dodaj z YouTub'a", "Dodaj ze Spotify"])

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
                        audio.export(mp3_buffer, format="mp3", bitrate="256k")
                    
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
                rec_audio.export(audio, format="mp3", bitrate="128k")  # Eksport do formatu MP3
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
            url = None
            query = None
            if st.button("Wczytaj",use_container_width=True, key="b_yt"):
                if youtube_url:
                    try:
                        url = youtube_url
                        with st.spinner("Pobieranie wideo z YouTube..."):
                            print("Rozpoczynam pobieranie...")
                            download_from_youtube(url,query,str(path_mp3))
                            print("Proces pobierania zakończony.")
                            

                        # Konwersja audio na MP3
                        with st.spinner("Konwertowanie pliku do formatu MP3..."):
                            audio = AudioSegment.from_file(path_mp3)
                            mp3_buffer = BytesIO()
                            audio.export(mp3_buffer, format="mp3", bitrate="256k")  # Konwersja do MP3 z bitrate 320 kbps

                        # Zapis pliku MP3 na dysku
                        with open(path_mp3, "wb") as f:
                            f.write(mp3_buffer.getvalue())
                        st.success("Plik został zapisany jako 'new.mp3'.")

                    except Exception as e:
                        # st.write("")
                        st.error(f"youtube Wystąpił błąd: {e}")
##########
        with add_spotify:
            st.subheader("Pobierz Muzykę ze Spotify")
            # Wprowadzenie linku Spotify
            spotify_link = st.text_input("Wklej link do utworu, albumu lub playlisty Spotify:")
            url = None
            query = None
            if st.button("Wczytaj",use_container_width=True, key="b_sf"):
                if spotify_link:
                    query = get_spotify_track(spotify_link)

                if query:
                    try:
                        with st.spinner("Pobieranie wideo z YouTube..."):
                            print("Rozpoczynam pobieranie...")
                            download_from_youtube(url, query, str(path_mp3))
                            print("Proces pobierania zakończony.")
                        # Konwersja audio na MP3
                        with st.spinner("Konwertowanie pliku do formatu MP3..."):
                            audio = AudioSegment.from_file(path_mp3)
                            mp3_buffer = BytesIO()
                            audio.export(mp3_buffer, format="mp3", bitrate="256k")  # Konwersja do MP3 z bitrate 320 kbps

                        # Zapis pliku MP3 na dysku
                        with open(path_mp3, "wb") as f:
                            f.write(mp3_buffer.getvalue())
                        st.success("Plik został zapisany jako 'new.mp3'.")
                    except Exception as e:
                        # st.write("")
                        st.error(f"spotify Wystąpił błąd: {e}")
            # else:
            #     st.error("Nie znaleziono utworów do pobrania.")



##########
        if (path_mp3.exists()) and (path_mp3.is_file()): #uploaded_file or rec_audio or youtube_url:
            st.audio(str(path_mp3))

            if st.button("Wczytaj nowy",use_container_width=True):
                st.session_state.uploaded_mp3 = None
                st.session_state.new = True
                st.session_state.current_menu = "page_addnew"
                st.rerun()
            if st.button("Informacja o utworze",use_container_width=True):
                st.session_state.uploaded_mp3 = str(path_mp3)
                st.session_state.current_menu = "page_info"
                st.rerun()
            if st.button("Przejdź do separacji ścieżek",use_container_width=True):
                st.session_state.uploaded_mp3 = str(path_mp3)
                st.session_state.current_menu = "page_sep"
                # st.rerun()
                        
    else:
        if (path_mp3.exists()) and (path_mp3.is_file()):
            st.subheader("Plik został już wczytany")
            st.audio(str(path_mp3)) 

            if st.button("Wczytaj nowy",use_container_width=True):
                st.session_state.uploaded_mp3 = None
                st.session_state.new = True
                st.session_state.current_menu = "page_addnew"
                st.rerun()
            if st.button("Informacja o utworze",use_container_width=True):
                st.session_state.current_menu = "page_info"
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