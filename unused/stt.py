import ssl
import certifi
import whisper
import os

# ----------------------------
# Step 1: Ensure SSL won't block anything (still safe)
# ----------------------------
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# ----------------------------
# Step 2: Audio file path
# ----------------------------
audio_path = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/audio/12.mp4 - 012 - Exercise 1 - Pure HTML Media Player.mp3"

if not os.path.isfile(audio_path):
    raise FileNotFoundError(f"Audio file not found: {audio_path}")

# ----------------------------
# Step 3: Load Whisper model offline
# Make sure the model files are already downloaded into ~/.cache/whisper/large-v2/
# ----------------------------
model = whisper.load_model("large-v2", download_root=os.path.expanduser("~/.cache/whisper"))

# ----------------------------
# Step 4: Transcribe & translate Hindi audio to English
# ----------------------------
result = model.transcribe(
    audio_path,
    language="hi",
    task="translate"
)

# ----------------------------
# Step 5: Print and save transcription
# ----------------------------
print("🔊 Translated Text:\n")
print(result["text"])

output_file = os.path.splitext(audio_path)[0] + "_translated.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(result["text"])

print(f"\n✅ Transcription saved to: {output_file}")
