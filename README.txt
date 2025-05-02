# 📁 Structure (all files inside a folder `web_app/`)
#
# web_app/
# ├── app.py               <- FastAPI backend
# ├── whisper_utils.py     <- Whisper transcription
# ├── llama3_utils.py      <- Few-shot report generator
# ├── docx_utils.py        <- DOCX formatter
# └── static/
#     └── index.html        <- Frontend UI
#
# To start the web app, run: 
# conda activate t5-vet-finetune
# uvicorn app:app --host 0.0.0.0 --port 8000