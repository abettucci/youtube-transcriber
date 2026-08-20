from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import youtube, llm, cache

router = APIRouter()


class SummaryRequest(BaseModel):
    url: str
    lang: str = "es"


@router.post("/summary")
def get_summary(req: SummaryRequest):
    try:
        video_id = youtube.extract_video_id(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cached = cache.get_cached(video_id)
    if cached and cached.get("summary"):
        return {
            "transcript": cached["transcript"],
            "summary": cached["summary"],
            "method": cached["method"],
            "cached": True,
        }

    try:
        if cached:
            transcript_text = cached["transcript"]
            method = cached["method"]
        else:
            result = youtube.get_transcript(video_id, lang=req.lang)
            transcript_text = result["text"]
            method = result["method"]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo obtener la transcripción: {e}")

    try:
        summary = llm.summarize(transcript_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al resumir: {e}")

    cache.save_cache(video_id, transcript_text, summary, method)

    return {
        "transcript": transcript_text,
        "summary": summary,
        "method": method,
        "cached": False,
    }
