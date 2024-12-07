# page_addnew.py

import streamlit as st
from audiorecorder import audiorecorder
from dotenv import dotenv_values
from pydub import AudioSegment
from yt_dlp import YoutubeDL
from pathlib import Path
from io import BytesIO
import browser_cookie3
import requests

env = dotenv_values(".env")

if 'WEBSHARE_KEY' in st.secrets:
    env['WEBSHARE_KEY'] = st.secrets['WEBSHARE_KEY']
if 'WEBSHARE_USER' in st.secrets:
    env['WEBSHARE_USER'] = st.secrets['WEBSHARE_USER']
if 'WEBSHARE_PASS' in st.secrets:
    env['WEBSHARE_PASS'] = st.secrets['WEBSHARE_PASS']
# Ścieżka do wyników
#######################################
def fetch_cookies(domain_name=None):
    """
    Pobiera cookies z Chrome, Firefox i Edge.
    """
    cookies = []
    try:
        cookies.extend(browser_cookie3.chrome(domain_name=domain_name))
        print("Cookies z Chrome pobrane.")
    except Exception as e:
        print(f"Błąd pobierania cookies z Chrome: {e}")

    try:
        cookies.extend(browser_cookie3.firefox(domain_name=domain_name))
        print("Cookies z Firefox pobrane.")
    except Exception as e:
        print(f"Błąd pobierania cookies z Firefox: {e}")

    try:
        cookies.extend(browser_cookie3.edge(domain_name=domain_name))
        print("Cookies z Edge pobrane.")
    except Exception as e:
        print(f"Błąd pobierania cookies z Edge: {e}")

    return cookies

def save_cookies_to_file(cookies, file_name):
    """
    Zapisuje cookies w formacie Netscape do pliku.
    """
    try:
        with open(file_name, "w") as file:
            file.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                file.write(
                    f"{cookie.domain}\t"
                    f"{str(cookie.secure).upper()}\t"
                    f"{cookie.path}\t"
                    f"{str(cookie.httpOnly).upper()}\t"
                    f"{cookie.expires}\t"
                    f"{cookie.name}\t"
                    f"{cookie.value}\n"
                )
        print(f"Cookies zapisane do pliku {file_name}")
    except Exception as e:
        print(f"Błąd zapisywania cookies do pliku: {e}")

###########################################################
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
                    domain = "youtube.com"  # Możesz zmienić domenę, np. na "example.com"
                    cookies = fetch_cookies(domain_name=domain)
                    
                    # Usunięcie duplikatów na podstawie nazwy ciasteczka i domeny
                    unique_cookies = {f"{cookie.domain}:{cookie.name}": cookie for cookie in cookies}.values()
                    
                    save_cookies_to_file(unique_cookies, "merged_cookies.txt")
                    
                    # Wprowadź swój klucz API
                    # api_key = env['WEBSHARE_KEY']
                    username = env['WEBSHARE_USER']
                    password = env['WEBSHARE_PASS']
                    # api_client = ApiClient(api_key)
                    # proxies = api_client.get_proxy_list()
                    # selected_proxy = proxies.get_results[0]
                    # proxy_url = f"http://{selected_proxy.username}:{selected_proxy.password}@{selected_proxy.proxy_address}:{selected_proxy.port}"
                    
                    proxy_url = f"http://{username}:{password}@107.172.163.27:6543"
                    # Pobieranie wideo z YouTube
                    # st.write(proxy_url)
                    with st.spinner("Pobieranie wideo z YouTube..."):
                        ydl_opts = {
                            "format": "bestaudio",
                            "cookies": "cookies.txt",
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
                            "proxy": proxy_url,
                            # "proxy": "socks4://217.145.199.47:56746",
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