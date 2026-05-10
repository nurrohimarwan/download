import streamlit as st
import yt_dlp
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Video Downloader", page_icon="📥")

# --- FUNGSI MESIN DOWNLOAD ---
def download_video(url, only_audio=False, resolusi="720p"):
    res_map = {"1080p": "137", "720p": "136", "480p": "135", "360p": "134"}
    format_id = res_map.get(resolusi, "best")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'ffmpeg_location': './', 
    }

    if only_audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': f"{format_id}+bestaudio/best",
            'merge_output_format': 'mp4',
        })

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            path_akhir = os.path.splitext(filename)[0] + (".mp3" if only_audio else ".mp4")
            return path_akhir
    except Exception:
        return None

# --- TAMPILAN WEB ---
st.title("VIDEO DOWNLOADER")
st.write("Bisa mendownload video dari beragam macam link")

# Inisialisasi memori tombol
if 'file_siap' not in st.session_state:
    st.session_state.file_siap = None

mode = st.radio("Mau video (mp4) atau music (mp3):", ["Video (MP4)", "Music (MP3)"])
is_mp3 = mode == "Music (MP3)"

url = st.text_input("Tempat taruh link:", placeholder="Tempel link di sini...")

res = "720p"
if not is_mp3:
    res = st.selectbox("Pilihan resolusi:", ["1080p", "720p", "480p", "360p"])

# --- LOGIKA TOMBOL GAS & UPLOAD ---
slot_tombol = st.empty()

if st.session_state.file_siap is None:
    if slot_tombol.button("GAS"):
        if url:
            slot_tombol.button("UPLOAD...", disabled=True) # Loading-nya Bos
            
            p = download_video(url, is_mp3, res)
            
            if p:
                st.session_state.file_siap = p
                st.rerun()
            else:
                st.error("Error, harap cek koneksi dan file, atau menghubungi developer")
                slot_tombol.button("GAS")
        else:
            st.warning("Isi link-nya dulu Bos!")

if st.session_state.file_siap:
    p = st.session_state.file_siap
    st.success("Sudah bos")
    
    with open(p, "rb") as f:
        st.download_button(
            label="📥 DOWNLOAD 📥",
            data=f,
            file_name=os.path.basename(p),
            mime="audio/mpeg" if is_mp3 else "video/mp4"
        )
    
    if st.button("Ulang lagi"):
        st.session_state.file_siap = None
        st.rerun()