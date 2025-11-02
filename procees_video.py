import os
import subprocess
import re

# ✅ Define input/output folders
video_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/Machine_learning_videos/Complete Machine Learning Course with Projects | Learn ML Step-by-Step"
audio_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/ML_audio"

# ✅ Create output folder if it doesn't exist
os.makedirs(audio_folder, exist_ok=True)

# ✅ Get all video files (skip hidden/system files)
files = [f for f in os.listdir(video_folder) if not f.startswith('.')]

# ✅ Process each file
for file in files:
    try:
        # Extract tutorial number (any number before '-' or 'Part X')
        match = re.search(r"(\d+)\s*-\s*|Part\s*(\d+)", file, re.IGNORECASE)
        if match:
            tutorial_number = match.group(1) or match.group(2)
        else:
            tutorial_number = "Unknown"

        # Remove extension and get clean title
        file_name = os.path.splitext(file)[0]

        # Debug info
        print(f"🎬 Processing: {file_name} (Tutorial #{tutorial_number})")

        # Input & output paths
        input_path = os.path.join(video_folder, file)
        output_path = os.path.join(audio_folder, f"{tutorial_number} - {file_name}.mp3")

        # ✅ Convert to MP3 using ffmpeg
        subprocess.run([
            "ffmpeg",
            "-i", input_path,
            "-vn",              # disable video
            "-ab", "192k",      # audio bitrate
            "-ar", "44100",     # sample rate
            "-y",               # overwrite
            output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        print(f"✅ Saved: {output_path}\n")

    except Exception as e:
        print(f"⚠️ Skipped: {file} (Error: {e})")
