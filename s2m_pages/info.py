# page_info.py

import streamlit as st
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
from dotenv import dotenv_values
from pydub import AudioSegment
import configparser
import requests
import base64
import time
import os
import hashlib
import hmac
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

env = dotenv_values(".env")

if 'SPOTIFY_CLIENT_ID' in st.secrets:
    env['SPOTIFY_CLIENT_ID'] = st.secrets['SPOTIFY_CLIENT_ID']
if 'SPOTIFY_CLIENT_SECRET' in st.secrets:
    env['SPOTIFY_CLIENT_SECRET'] = st.secrets['SPOTIFY_CLIENT_SECRET']
if 'PROXY_URL' in st.secrets:
    env['PROXY_URL'] = st.secrets['PROXY_URL']

if 'ACR_ACCESS_KEY' in st.secrets:
    env['ACR_ACCESS_KEY'] = st.secrets['ACR_ACCESS_KEY']
if 'ACR_SECRET_KEY' in st.secrets:
    env['ACR_SECRET_KEY'] = st.secrets['ACR_SECRET_KEY']

# Autoryzacja
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = env['SPOTIFY_CLIENT_ID'],
    client_secret = env['SPOTIFY_CLIENT_SECRET']
))


path_mp3 = ""
config_mp3 = ""

##############################################################
def load_info():
    """
    Ładuje ustawienia z pliku new.cfg.
    Jeśli plik nie istnieje, zwraca wartości domyślne.
    """
    config = configparser.ConfigParser(interpolation=None)  # Wyłączenie interpolacji
    if os.path.exists(config_mp3):
        config.read(config_mp3)
        
        # Zapis danych do st.session_state
        st.session_state['mp3_info'] = {
            "title": config["TRACK"].get("title"),
            "artist": config["TRACK"].get("artist"),
            "album": config["TRACK"].get("album"),
            "track_number": config["TRACK"].get("track_number"),
            "genres": config["TRACK"].get("genres"),
            "release_date": config["TRACK"].get("release_date"),
            "spotify_url": config["TRACK"].get("spotify_url"),
            "album_image": config["TRACK"].get("album_image")
        }

    else:
        config["TRACK"] = {
            "title": str(st.session_state["mp3_info"].get("title", "Unknown")),
            "artist": str(st.session_state["mp3_info"].get("artist", "Unknown")),
            "album": str(st.session_state["mp3_info"].get("album", "Unknown")),
            "track_number": str(st.session_state["mp3_info"].get("track_number", "")),
            "release_date": str(st.session_state["mp3_info"].get("release_date", "Unknown")),
            "genres": str(st.session_state["mp3_info"].get("genres", "Unknown")),
            "spotify_url": str(st.session_state["mp3_info"].get("spotify_url", None)),
            "album_image": str(st.session_state["mp3_info"].get("album_image", None))           
        }
        
    return config
#################
def save_info():
    """
    Zapisuje ustawienia do pliku setup.cfg.
    """
    config = configparser.ConfigParser(interpolation=None)  # Wyłączenie interpolacji

    config["TRACK"] = {
            "title": str(st.session_state["mp3_info"].get("title", "")),
            "artist": str(st.session_state["mp3_info"].get("artist", "")),
            "album": str(st.session_state["mp3_info"].get("album", "")),
            "track_number": str(st.session_state["mp3_info"].get("track_number", "")),
            "release_date": str(st.session_state["mp3_info"].get("release_date", "")),
            "genres": str(st.session_state["mp3_info"].get("genres", "")),
            "spotify_url": str(st.session_state["mp3_info"].get("spotify_url", "")),
            "album_image": str(st.session_state["mp3_info"].get("album_image", ""))           
        }

    with open(config_mp3, "w") as configfile:
        config.write(configfile)

##############################################################
def recognize_music(file_path, start_time=0, duration=10, max_attempts=5):
    try:
        # Konfiguracja
        access_key = env['ACR_ACCESS_KEY']
        access_secret = env['ACR_SECRET_KEY']
        requrl = 'https://identify-eu-west-1.acrcloud.com/v1/identify'
        http_method = 'POST'
        http_uri = '/v1/identify'
        data_type = 'audio'
        signature_version = '1'
        
        attempts = 0
        while attempts < max_attempts:
            # Przycinanie audio
            trimmed_path = Path("users") / st.session_state.username / "songs" / "new" / "trimmed.mp3"
            audio = AudioSegment.from_file(file_path)
            start_ms = start_time * 1000
            end_ms = start_ms + (duration * 1000)
            trimmed_audio = audio[start_ms:end_ms]
            trimmed_audio.export(trimmed_path, format="mp3")
        
            # Obliczanie sygnatury
            timestamp = str(int(time.time()))
            string_to_sign = f"{http_method}\n{http_uri}\n{access_key}\n{data_type}\n{signature_version}\n{timestamp}"
            sign = base64.b64encode(
                hmac.new(
                    access_secret.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    digestmod=hashlib.sha1
                ).digest()
            ).decode('utf-8')

            # Przygotowanie danych do wysłania
            with open(trimmed_path, 'rb') as f:
                file_data = f.read()
            files = {'sample': ('trimmed.mp3', file_data, 'audio/mpeg')}
            data = {
                'access_key': access_key,
                'sample_bytes': len(file_data),
                'timestamp': timestamp,
                'signature': sign,
                'data_type': data_type,
                'signature_version': signature_version
            }

            # Wysłanie żądania
            response = requests.post(requrl, files=files, data=data)
            # st.write(response)
            if response.status_code == 200:
                parsed_data = response.json()
                if "metadata" in parsed_data and "music" in parsed_data["metadata"]:
                    for track in parsed_data["metadata"]["music"]:
                        # Parsowanie danych utworu
                        title = track.get("title", "Nieznany tytuł")
                        artists = ", ".join([artist.get("name", "Nieznany artysta") for artist in track.get("artists", [])])
                        album = track.get("album", {}).get("name", "Nieznany album")
                        release_date = track.get("release_date", "Brak daty")
                        genres = ", ".join([genre.get("name", "Nieznany gatunek") for genre in track.get("genres", [])])
                        spotify_url = track.get("external_metadata", {}).get("spotify", {}).get("track", {}).get("id")
                        album_image = track.get("external_metadata", {}).get("spotify", {}).get("album", {}).get("id")
                        album_image = f"https://i.scdn.co/image/{album_image}" if album_image else None

                        # Zapis danych
                        st.session_state['mp3_info'] = {
                            "title": title,
                            "track_number": "",
                            "artist": artists,
                            "album": album,
                            "genres": genres,
                            "release_date": release_date,
                            "spotify_url": spotify_url,
                            "album_image": album_image
                        }

                        if spotify_url:
                            get_spotify_track(spotify_url)
                        return True
                else:
                    st.warning(f"Nie znaleziono wyników dla fragmentu {attempts + 1}.")
                    start_time += duration
                    attempts += 1
            else:
                st.error(f"Error {response.status_code}: {response.text}")
                return False

        st.error("Nie udało się rozpoznać utworu po kilku próbach.")
        return False
    
    except Exception as e:
        st.error(f"Wystąpił błąd: {e}")
        return False

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


        print(f"Utwór: {artist} - {title} z Albumu {album} - {release_date}" )
        return f"{artist} - {title} {album} {release_date}"
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o utworze: {e}")
        return None

###########################################################

##############################################################
def show_page():
    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    path_mp3 = PATH_UPLOAD / "new.mp3"
    config_mp3 = PATH_UPLOAD / "new.cfg"
    st.title(":musical_note: Song info")

    song = ""
    if st.session_state['mp3_info']['title'] != "":
        song =str(f"{st.session_state['mp3_info']['artist']} - {st.session_state['mp3_info']['title']}")

    st.header(f"Inormacje o utworze: {song}")
    info= load_info()
    
    st.write("---")

    c0, c1 = st.columns([6,4]) #([8,2])
    with c0:
        # if st.session_state['mp3_info']['album_image']:
        #     st.image(st.session_state['mp3_info']['album_image'])
        # Sprawdź, czy w danych znajduje się ścieżka do obrazu
        if 'album_image' in st.session_state['mp3_info'] and st.session_state['mp3_info']['album_image']:
            st.image(st.session_state['mp3_info']['album_image'], caption="Okładka albumu")
        else:
            # Jeśli brak ścieżki, pozwól użytkownikowi wgrać obraz z komputera
            uploaded_image = st.file_uploader("Wgraj obraz dla albumu", type=["jpg", "png", "jpeg"])
            
            if uploaded_image:
                save_path = PATH_UPLOAD / "new.jpg"
                with open(save_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                st.write(save_path)
                st.session_state['mp3_info']['album_image'] = str(save_path)
                st.rerun()
                # st.image(save_path, caption="Wgrany obraz dla albumu")
            else:
                st.warning("Brak okładki albumu. Wgraj obraz lub podaj ścieżkę.")
        
    with c1:
        with st.container(border=False):
            artist = st.text_input("Artysta", value=st.session_state['mp3_info'].get("artist", ""), key="artist")
            if artist:
                st.session_state['mp3_info']['artist'] = artist
            album = st.text_input("Album", value=st.session_state['mp3_info'].get("album", ""), key="album")
            if album:
                st.session_state['mp3_info']['album'] = album
            release_date = st.text_input("Data wydania", value=st.session_state['mp3_info'].get("release_date", ""), key="release_date")
            if release_date:
                st.session_state['mp3_info']['release_date'] = release_date
            title = st.text_input("Utwór", value=st.session_state['mp3_info'].get("title", ""), key="title")
            if title:
                st.session_state['mp3_info']['title'] = title
            track_number = st.text_input("Nr Utworu", value=st.session_state['mp3_info'].get("track_number", ""), key="track_number")
            if track_number:
                st.session_state['mp3_info']['track_number'] = track_number

    if st.button("Wczytaj nowy",use_container_width=True):
        st.session_state.current_menu = "page_addnew"
        st.rerun()
    if st.button("Pobierz informacje o utworze",use_container_width=True):
        with st.spinner("W trakcie rozpoznawania"):
            recognize_music(str(path_mp3))
            st.rerun()
    
    if st.button("Zapisz informacje o utworze",use_container_width=True):
        with st.spinner("Zapisywanie"):
            # save_info()
            audio = MP3(path_mp3, ID3=EasyID3)
            # Dodawanie metadanych
            audio["title"] = st.session_state['mp3_info']['title']
            audio["artist"] = st.session_state['mp3_info']['artist']
            audio["album"] = st.session_state['mp3_info']['album']
            audio["genre"] = st.session_state['mp3_info']['genres']
            audio["tracknumber"] = st.session_state['mp3_info']['track_number']
            audio["date"] = st.session_state['mp3_info']['release_date']
            # Zapisz zmiany
            audio.save()
            cover_path = st.session_state['mp3_info']['album_image']
            save_path = PATH_UPLOAD / "new.jpg"
            if cover_path != str(save_path):
                try:
                    response = requests.get(cover_path)
                    response.raise_for_status()  # Sprawdzenie, czy żądanie zakończyło się sukcesem
                    # save_path = PATH_UPLOAD / "new.jpg"
                    with open(save_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Obrazek zapisano jako: {save_path}")
                except requests.exceptions.RequestException as e:
                    print(f"Błąd podczas pobierania obrazka: {e}")
            
            # st.image(st.session_state['mp3_info']['album_image'])
            audio = MP3(path_mp3, ID3=ID3)
            # Dodaj obrazek jako okładkę albumu
            audio.tags.add(
                APIC(
                    encoding=3,        # UTF-8
                    mime="image/jpeg", # Typ MIME obrazka
                    type=3,            # Okładka przednia (3)
                    desc="Cover",
                    data=open(save_path, "rb").read()
                )
            )
            audio.save()
 
        # recognize_music(str(path_mp3))

    if st.button("Przejdź do separacji ścieżek",use_container_width=True):
            st.session_state.current_menu = "page_sep"
            st.rerun()

    if (path_mp3.exists()) and (path_mp3.is_file()): #uploaded_file or rec_audio or youtube_url:
        
        st.audio(str(path_mp3))
        
        # Odczytaj zawartość pliku
        with open(path_mp3, "rb") as file:
            file_data = file.read()
        # Pobieranie pliku w Streamlit
        metadata = {
            "track_nr": st.session_state['mp3_info']['track_number'],
            "title": st.session_state['mp3_info']['title'],
            "artist": st.session_state['mp3_info']['artist'],
            "album": st.session_state['mp3_info']['album']
        }

        # track_nr = st.session_state['mp3_info']['track_number']
        # title = st.session_state['mp3_info']['title']
        # artist = st.session_state['mp3_info']['artist']
        # album = st.session_state['mp3_info']['album']
        
        mp3_format = st.text_input("Podaj format nazwy pliku {track_nr} {title} - {artist} - {album}", value=str(st.session_state.get("mp3_download_format", "")))
        if mp3_format:
            st.session_state.mp3_download_format = mp3_format

        # Zastąpienie zmiennych w formacie rzeczywistymi wartościami
        try:
            mp3_download = mp3_format.format(**metadata) + ".mp3"
        except KeyError as e:
            st.error(f"Brakuje wartości dla zmiennej: {e}")
            mp3_download = "default.mp3"

        st.download_button(
            label="Pobierz plik",
            data=file_data,
            file_name= mp3_download,  # Nowa nazwa pliku
            mime="audio/mp3"
        )
        # if st.button("Pobierz MP3",use_container_width=True):
        #     with st.spinner("Pobieranie"):
        #         # Odczytaj zawartość pliku
        #         with open(path_mp3, "rb") as file:
        #             file_data = file.read()