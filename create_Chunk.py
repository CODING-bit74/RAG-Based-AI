import whisper
import json
import os

# ----------------------------
# Step 1: Load Whisper model
# ----------------------------
model = whisper.load_model("large-v2", download_root=os.path.expanduser("~/.cache/whisper"))

# ----------------------------
# Step 2: Define input/output folders
# ----------------------------
audio_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/audio"
output_folder = "/Users/arpitmishra/Desktop/Walmart Sales Forecast/RAG-Based-AI/jsons"

# Create output folder if it doesn’t exist
os.makedirs(output_folder, exist_ok=True)

# ----------------------------
# Step 3: Process each audio file
# ----------------------------
audios = [f for f in os.listdir(audio_folder) if f.lower().endswith((".mp3", ".wav", ".m4a", ".mp4"))]

for audio in audios:
    try:
        # Expect filenames like: "12_Exercise1.mp3"
        if "_" in audio:
            number = audio.split("_")[0]
            title = os.path.splitext("_".join(audio.split("_")[1:]))[0]  # Handle names with multiple underscores
        else:
            number = "unknown"
            title = os.path.splitext(audio)[0]

        print(f"\n🎧 Processing: {audio} → {title}")

        # ----------------------------
        # Step 4: Transcribe & translate Hindi → English
        # ----------------------------
        result = model.transcribe(
            audio=os.path.join(audio_folder, audio),
            language="hi",
            task="translate",
            word_timestamps=False
        )

        # ----------------------------
        # Step 5: Create structured output
        # ----------------------------
        chunks = []
        for segment in result["segments"]:
            chunks.append({
                "number": number,
                "title": title,
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"]
            })

        chunks_with_metadata = {
            "number": number,
            "title": title,
            "full_text": result["text"],
            "chunks": chunks
        }

        # ----------------------------
        # Step 6: Save as JSON
        # ----------------------------
        output_path = os.path.join(output_folder, f"{os.path.splitext(audio)[0]}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved JSON: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {audio}: {e}")

print("\n🎉 All audios processed successfully!")
