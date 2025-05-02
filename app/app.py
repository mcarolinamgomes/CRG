from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from whisper_utils import transcribe_audio
from llama3_utils import generate_report
from docx_utils import generate_pretty_docx
import uuid
import shutil


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    # Step 1: Save audio file
    temp_audio_path = f"temp_{uuid.uuid4().hex}.mp3"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"🔊 Transcribing: {temp_audio_path}")
    transcription = transcribe_audio(temp_audio_path)
    print("🔍 Generating report for input transcription...")

    # Step 2: Generate report as JSON string
    json_report = generate_report(transcription, "few_shot_data.jsonl")

    # Step 3: Generate DOCX file
    output_docx = f"report_{uuid.uuid4().hex}.docx"
    generate_pretty_docx(json_report, output_path=output_docx)

    # Step 4: Clean up audio file
    os.remove(temp_audio_path)

    # Step 5: Return DOCX as proper file response
    return FileResponse(
        output_docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="relatorio_clinico.docx"
    )



@app.get("/download/{filename}")
def download_docx(filename: str):
    return FileResponse(path=filename, filename=filename)
