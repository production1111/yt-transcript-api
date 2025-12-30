from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = FastAPI()

class Req(BaseModel):
    url: str
    lang: str | None = None

def extract_video_id(url: str) -> str | None:
    patterns = [
        r"v=([A-Za-z0-9_-]{11})",
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"shorts/([A-Za-z0-9_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

@app.post("/transcript")
def transcript(req: Req):
    video_id = extract_video_id(req.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        if req.lang:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=[req.lang])
        else:
            data = YouTubeTranscriptApi.get_transcript(video_id)

        text = " ".join([x["text"] for x in data]).strip()
        return {"transcript": text, "video_id": video_id}

    except (TranscriptsDisabled, NoTranscriptFound):
        raise HTTPException(status_code=404, detail="Transcript not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
