import streamlit as st
import yt_dlp
import os
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Video Downloader", page_icon="📥")

# --- FUNGSI MESIN DOWNLOAD ---
def download_video(url, only_audio=False, resolusi="720p"):
    res_map = {"1080p": "137", "720p": "136", "480p": "135", "360p": "134"}
    format_id = res_map.get(resolusi, "best")

    # Wadah untuk progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Fungsi internal untuk menangkap progres dari yt-dlp
    def hook(d):
        if d['status'] == 'downloading':
            try:
                # Menghitung persentase
                p = d.get('_percent_str', '0%').replace('%','')
                p_float = float(p) / 100
                progress_bar.progress(p_float)
                status_text.text(f"Downloading: {d.get('_percent_str', '0%')} | Speed: {d.get('_speed_str', 'N/A')}")
            except:
                pass
        if d['status'] == 'finished':
            progress_bar.progress(1.0)
            status_text.text("Download Selesai! Sedang mengonversi file...")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'progress_hooks': [hook],
        # Tambahkan baris di bawah ini untuk "menyamar" jadi browser Chrome
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
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
            
            # Beri jeda dikit biar user sempat lihat bar 100%
            time.sleep(1) 
            progress_bar.empty()
            status_text.empty()
            
            return path_akhir, None
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        return None, str(e)

# --- TAMPILAN WEB ---
st.title("VIDEO DOWNLOADER")
st.write("Bisa mendownload video dari beragam macam link")

if 'file_siap' not in st.session_state:
    st.session_state.file_siap = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'pesan_error' not in st.session_state:
    st.session_state.pesan_error = None

mode = st.radio("Mau video (mp4) atau music (mp3):", ["Video (MP4)", "Music (MP3)"])
is_mp3 = mode == "Music (MP3)"

url = st.text_input("Tempat taruh link:", placeholder="Tempel link di sini...")

res = "720p"
if not is_mp3:
    res = st.selectbox("Pilihan resolusi:", ["1080p", "720p", "480p", "360p"])

st.write("---")

# --- TOMBOL KIRI & KANAN ---
col_kiri, col_kanan = st.columns(2)

disable_upload = st.session_state.file_siap is not None or st.session_state.is_processing

if col_kiri.button("🚀 GAS / UPLOAD", use_container_width=True, disabled=disable_upload):
    if url:
        st.session_state.is_processing = True
        st.session_state.pesan_error = None
        st.rerun()
    else:
        st.warning("Isi link-nya dulu Bos!")

# Tampilan saat proses (Bar muncul di sini)
if st.session_state.is_processing:
    p, err = download_video(url, is_mp3, res)
    if p:
        st.session_state.file_siap = p
        st.session_state.is_processing = False
        st.rerun()
    else:
        st.session_state.pesan_error = err
        st.session_state.is_processing = False
        st.rerun()

if st.session_state.file_siap:
    p = st.session_state.file_siap
    with open(p, "rb") as f:
        col_kanan.download_button(
            label="📥 DOWNLOAD SEKARANG",
            data=f,
            file_name=os.path.basename(p),
            mime="audio/mpeg" if is_mp3 else "video/mp4",
            use_container_width=True
        )

# --- ERROR & RESET ---
if st.session_state.pesan_error:
    st.error(f"⚠️ **TERJADI ERROR:**\n\n{st.session_state.pesan_error}")
    if st.button("Coba Lagi"):
        st.session_state.pesan_error = None
        st.rerun()

if st.session_state.file_siap:
    if st.button("Hapus & Download Link Lain"):
        if os.path.exists(st.session_state.file_siap):
            os.remove(st.session_state.file_siap)
        st.session_state.file_siap = None
        st.rerun()

# --- COPYRIGHT ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        © 2026 arwan's_lab | Physics Mechanic Edition
    </div>
    """, 
    unsafe_allow_html=True
)
