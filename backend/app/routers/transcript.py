from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import youtube, cache

router = APIRouter()


class TranscriptRequest(BaseModel):
    url: str
    lang: str = "es"


@router.post("/transcript")
def get_transcript(req: TranscriptRequest):
    try:
        video_id = youtube.extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cached = cache.get_cached(video_id)
    if cached:
        return {
            "transcript": cached["transcript"],
            "method": cached["method"],
            "word_count": len(cached["transcript"].split()),
            "cached": True,
        }

    try:
        result = youtube.get_transcript(video_id, lang=req.lang)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo obtener la transcripción: {e}")

    cache.save_cache(video_id, result["text"], None, result["method"])

    return {
        "transcript": result["text"],
        "method": result["method"],
        "word_count": result["word_count"],
        "cached": False,
    }
