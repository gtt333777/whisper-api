from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import whisper
import requests
import tempfile

app = FastAPI()
model = whisper.load_model("base")  # You can change to "tiny" or "medium"

class TranscriptionRequest(BaseModel):
    fileUrl: str
    fileName: str

@app.post("/transcribe")
async def transcribe(req: TranscriptionRequest):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            r = requests.get(req.fileUrl)
            temp_file.write(r.content)
            temp_file.flush()

            result = model.transcribe(temp_file.name)

            lrc_lines = []
            for seg in result["segments"]:
                m, s = divmod(seg["start"], 60)
                timestamp = f"[{int(m):02}:{s:05.2f}]"
                lrc_lines.append(f"{timestamp} {seg['text'].strip()}")

            return JSONResponse({"lrcText": "\n".join(lrc_lines)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
