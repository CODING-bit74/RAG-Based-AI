# Import the os module for file and directory operations
import os
# Import subprocess module to run external commands
import subprocess

# ✅ Define input/output folders
# Set the path to the directory containing video files
video_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/videos"
# Set the path to the directory where audio files will be saved
audio_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/audio"

# ✅ Create output folder if it doesn't exist
# Create the audio folder if it doesn't exist, without raising an error if it already exists
os.makedirs(audio_folder, exist_ok=True)

# ✅ Get all video files
# Get a list of all files in the video folder
files = os.listdir(video_folder)

# Iterate through each file in the video folder
for file in files:
    # Try to process each file, handling potential errors
    try:
        # ✅ Extract tutorial number and file name safely
        # Extract the tutorial number from the filename (format: "XXX - Title #N")
        tutorial_number = file.split(" [")[0].split(" #")[1]
        # Extract the main title of the file (before the "｜" character)
        file_name = file.split(" ｜ ")[0]

        # Print the extracted tutorial number and file name for debugging
        print(tutorial_number, file_name)

        # ✅ Convert video to MP3
        # Create the full path to the input video file
        input_path = os.path.join(video_folder, file)
        # Create the full path for the output audio file with formatted name
        output_path = os.path.join(audio_folder, f"{tutorial_number} - {file_name}.mp3")

        # Run ffmpeg command to convert video to audio
        subprocess.run([
            # Command to execute
            "ffmpeg",
            # Input file parameter
            "-i", input_path,
            # Disable video stream in output
            "-vn",               # disable video
            # Set audio bitrate to 192kbps
            "-ab", "192k",       # set audio bitrate
            # Set audio sample rate to 44.1kHz (CD quality)
            "-ar", "44100",      # set sample rate
            # Overwrite output file if it already exists
            "-y",                # overwrite if exists
            # Output file path
            output_path
        ])

    # Handle the case where the filename format doesn't match expected pattern
    except IndexError:
        # Print a warning message for files that couldn't be processed
        print(f"⚠️ Skipped: {file} (naming format not matched)")
