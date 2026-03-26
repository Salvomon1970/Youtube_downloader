%%writefile app.py
import streamlit as st
import yt_dlp
import os
import re

st.title("Downloader Video YouTube")
st.write("Inserisci il link del video e seleziona la qualità desiderata per avviare il download.")

url = st.text_input("Link YouTube:")

opzioni_risoluzione = [
    "Migliore qualità (fino a 4K)", 
    "1080p", 
    "720p", 
    "Solo Audio (MP3)"
]
scelta = st.selectbox("Seleziona il formato e la risoluzione:", opzioni_risoluzione)

bottone_scarica = st.button("Scarica", type="primary")

progress_bar = st.empty()
status_text = st.empty()

def aggiorna_progresso(d):
    if d['status'] == 'downloading':
        try:
            percent_str = d.get('_percent_str', '0.0%')
            percent_str_clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
            percent = float(percent_str_clean.replace('%', ''))
            progress_bar.progress(int(percent))
            status_text.text(f"Download in corso: {percent_str_clean.strip()}")
        except Exception:
            pass
    elif d['status'] == 'finished':
        status_text.text("Elaborazione finale in corso con FFmpeg...")
        progress_bar.progress(100)

if bottone_scarica and url:
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [aggiorna_progresso],
        'quiet': True,
        'noprogress': True,
        'impersonate': 'chrome',
        'source_address': '0.0.0.0',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-Fetch-Mode': 'navigate'
        }
    }

    if scelta == "Migliore qualità (fino a 4K)":
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif scelta == "1080p":
        ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif scelta == "720p":
        ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'
    elif scelta == "Solo Audio (MP3)":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename_grezzo = ydl.prepare_filename(info_dict)
            
            if scelta == "Solo Audio (MP3)":
                filename_finale = os.path.splitext(filename_grezzo)[0] + ".mp3"
                mime_type = "audio/mpeg"
            else:
                filename_finale = os.path.splitext(filename_grezzo)[0] + ".mp4"
                mime_type = "video/mp4"
            
        status_text.success("Elaborazione completata! Clicca qui sotto per scaricare il file.")
        
        with open(filename_finale, "rb") as file_da_scaricare:
            dati_video = file_da_scaricare.read()
            
        st.download_button(
            label="Salva il file",
            data=dati_video,
            file_name=os.path.basename(filename_finale),
            mime=mime_type
        )
        
        os.remove(filename_finale)
        
    except Exception as e:
        status_text.error(f"Si è verificato un errore: {str(e)}")
elif bottone_scarica and not url:
    st.warning("Inserisci un link valido prima di procedere.")
