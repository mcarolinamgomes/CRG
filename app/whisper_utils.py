import whisper
import os

def transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")  # or "medium", "large" as needed
    print(f"🔊 Transcribing: {file_path}")
    result = model.transcribe(file_path, language='pt')
    return result["text"]

# Example usage
if __name__ == "__main__":
    transcript = transcribe_audio("luvvoice.com-20250430-s8YXYW.mp3")
    print("\n📝 Transcription Result:\n")
    print(transcript)
