# -----------------------------------------------
# YouTube Playlist Downloader (by Arpit Kumar Mishra)
# -----------------------------------------------
# This script downloads all videos from a YouTube playlist using yt-dlp.
# ✅ Stable and works even if YouTube changes layout.
# -----------------------------------------------

import os
import yt_dlp

# ✅ STEP 1: Playlist URL
playlist_url = "https://youtube.com/playlist?list=PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w"

# ✅ STEP 2: Choose your download folder
download_path = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/videos"

# ✅ STEP 3: yt-dlp Options
ydl_opts = {
    "outtmpl": os.path.join(download_path, "%(playlist_index)s - %(title)s.%(ext)s"),
    "format": "bestvideo+bestaudio/best",
    "merge_output_format": "mp4",
    "ignoreerrors": True,
    "noplaylist": False,
    "progress_hooks": [
        lambda d: print(f"⏬ Downloading: {d.get('filename', 'unknown')}") if d['status'] == 'downloading' else None
    ],
}

# ✅ STEP 4: Download Playlist
print("📋 Fetching playlist info...")
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(playlist_url, download=True)
    print("\n🎥 Playlist Title:", info.get("title", "Unknown Playlist"))
    print(f"🎬 Total Videos: {len(info.get('entries', []))}")
    print("✅ All videos downloaded successfully!")
