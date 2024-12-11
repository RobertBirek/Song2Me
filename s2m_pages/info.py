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

if "username" not in st.session_state:
    st.session_state.username = None
else:
    PATH_UPLOAD = Path("users") / st.session_state.username / "songs" / "new"
    path_mp3 = PATH_UPLOAD / "new.mp3"
    config_mp3 = PATH_UPLOAD / "new.cfg"

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
            "track_number": str(st.session_state["mp3_info"].get("track_number", None)),
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
            "title": str(st.session_state["mp3_info"].get("title", "Unknown")),
            "artist": str(st.session_state["mp3_info"].get("artist", "Unknown")),
            "album": str(st.session_state["mp3_info"].get("album", "Unknown")),
            "track_number": str(st.session_state["mp3_info"].get("track_number", None)),
            "release_date": str(st.session_state["mp3_info"].get("release_date", "Unknown")),
            "genres": str(st.session_state["mp3_info"].get("genres", "Unknown")),
            "spotify_url": str(st.session_state["mp3_info"].get("spotify_url", None)),
            "album_image": str(st.session_state["mp3_info"].get("album_image", None))           
        }

    with open(config_mp3, "w") as configfile:
        config.write(configfile)

##############################################################
def recognize_music(file_path, start_time=30, duration=10):
    # Konfiguracja
    access_key = env['ACR_ACCESS_KEY']
    access_secret = env['ACR_SECRET_KEY']
    requrl = 'https://identify-eu-west-1.acrcloud.com/v1/identify'
    http_method = 'POST'
    http_uri = '/v1/identify'
    data_type = 'audio'
    signature_version = '1'
    timestamp = str(int(time.time()))
 
    # trimm 10sek
    filet_path = Path("users") / st.session_state.username / "songs" / "new" / "trimmed.mp3"
    # file_path = "trimmed.mp3"
    # Wczytanie pliku audio
    audio = AudioSegment.from_file(file_path)
    # Przycinanie do pierwszych `duration` sekund
    start_ms = start_time * 1000  # Konwersja na milisekundy
    end_ms = start_ms + (duration * 1000)
    trimmed_audio = audio[start_ms:end_ms]  # Konwersja na milisekundy
    trimmed_audio.export(filet_path, format="mp3")

    # Wczytanie pliku audio
    with open(filet_path, 'rb') as f:
        sample_bytes = os.path.getsize(filet_path)
        filet_data = f.read()

    # Obliczanie sygnatury
    string_to_sign = f"{http_method}\n{http_uri}\n{access_key}\n{data_type}\n{signature_version}\n{timestamp}"
    sign = base64.b64encode(hmac.new(access_secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest()).decode('utf-8')


      # Przygotowanie danych do wysłania
    # Przygotowanie danych do wysłania
    files = {
        'sample': (os.path.basename(filet_path), filet_data, 'audio/mpeg')
    }
    data = {
        'access_key': access_key,
        'sample_bytes': sample_bytes,
        'timestamp': timestamp,
        'signature': sign,
        'data_type': data_type,
        'signature_version': signature_version
    }

    # Wysłanie żądania
    response = requests.post(requrl, files=files, data=data)
    parsed_data = response.json()
    msg = parsed_data["status"]["msg"]
    if msg == "No result":
        start_ms = start_ms * 2
        recognize_music(file_path, start_ms)
    if response.status_code == 200:
        parsed_data = response.json()
        # st.write("Odpowiedź z API:", parsed_data)
        spotify_url = None
        for track in parsed_data["metadata"]["music"]:
            title = track.get("title", "Nieznany tytuł")
            artists = ", ".join([artist.get("name") for artist in track.get("artists", [])])
            album = track.get("album", {}).get("name", "Nieznany album")
            release_date = track.get("release_date", "Brak daty")
            genres = ", ".join([genre.get("name") for genre in track.get("genres", [])])
            spotify_track_id = track.get("external_metadata", {}).get("spotify", {}).get("track", {}).get("id")
            spotify_url = track.get("external_metadata", {}).get("spotify", {}).get("track", {}).get("id")
            # Link do obrazu albumu
            spotify_album_id = track.get("external_metadata", {}).get("spotify", {}).get("album", {}).get("id")
            album_image = f"https://i.scdn.co/image/{spotify_album_id}" if spotify_album_id else None
            
            # print(f"Tytuł: {title}")
            # print(f"Artyści: {', '.join(artists)}")
            # print(f"Album: {album}")
            # print(f"Data wydania: {release_date}")
            # print(f"Gatunki: {', '.join(genres)}")
            # if spotify_url:
                # get_spotify_track(spotify_url)
            #     print(f"Link do Spotify: https://open.spotify.com/track/{spotify_url}")
            # print("-" * 30)
            
            # Zapis danych do st.session_state
            st.session_state['mp3_info'] = {
                "title": title,
                "artist": artists,
                "album": album,
                "genres": genres,
                "release_date": release_date,
                "spotify_url": spotify_url,
                "album_image": album_image
            }
        
        if spotify_url:
            get_spotify_track(spotify_url)

        
        return True #response.json()
    else:
        # print(f"error: {response.status_code}, message: {response.text}")
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
    st.title(":musical_note: Song info")
    st.header("Inormacje o utworze")
    info= load_info()
    
    # save_info()
    if st.session_state['mp3_info']['title']:
        st.write("---")
        st.subheader(f"{st.session_state['mp3_info']['artist']} - {st.session_state['mp3_info']['title']}")
        st.write("---")

    c0, c1 = st.columns([6,4]) #([8,2])
    with c0:
        if st.session_state['mp3_info']['album_image']:
            st.image(st.session_state['mp3_info']['album_image'])
        
        # st.write(st.session_state['mp3_info']['title'])

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
            track_number = st.text_input("Utwór", value=st.session_state['mp3_info'].get("track_number", ""), key="track_number")
            if track_number:
                st.session_state['mp3_info']['track_number'] = track_number

    if st.button("Wczytaj nowy",use_container_width=True):
        st.session_state.current_menu = "page_addnew"
        st.rerun()
    if st.button("Pobierz informacje o utworze",use_container_width=True):
        with st.spinner("W trakcie rozpoznawania"):
            recognize_music(str(path_mp3))
    
    if st.button("Zapisz informacje o utworze",use_container_width=True):
        with st.spinner("Zapisywanie"):
            save_info()
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
            if cover_path:
                try:
                    response = requests.get(cover_path)
                    response.raise_for_status()  # Sprawdzenie, czy żądanie zakończyło się sukcesem
                    save_path = PATH_UPLOAD / "new.jpg"
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