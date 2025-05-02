from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from app.whisper_utils import transcribe_audio  # ✅ if inside an `app/` folder
from app.llama3_utils import generate_report
from app.docx_utils import generate_pretty_docx
import uuid
import shutil
from pathlib import Path

app = FastAPI()

# Use absolute path based on current file location
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_frontend():
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))



@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Save audio to /tmp/
        temp_audio_path = f"/tmp/temp_{uuid.uuid4().hex}.mp3"
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"🔊 Transcribing: {temp_audio_path}")

        transcription = transcribe_audio(temp_audio_path)
        print("🔍 Transcription complete. Generating report...")

        json_report = generate_report(transcription, "few_shot_data.jsonl")
        output_docx = f"/tmp/report_{uuid.uuid4().hex}.docx"

        print("📄 Creating DOCX report...")
        generate_pretty_docx(json_report, output_path=output_docx)

        print("✅ Report generated. Sending file.")
        return FileResponse(output_docx, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="relatorio_clinico.docx")

    except Exception as e:
        print(f"❌ Error: {e}")
        return HTMLResponse(content=f"Erro interno: {str(e)}", status_code=500)


@app.get("/download/{filename}")
def download_docx(filename: str):
    return FileResponse(path=filename, filename=filename)
