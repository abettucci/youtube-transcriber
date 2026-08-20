import os
from supabase import create_client, Client

_client: Client | None = None


def _get_client() -> Client | None:
    global _client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    if _client is None:
        _client = create_client(url, key)
    return _client


def get_cached(video_id: str) -> dict | None:
    client = _get_client()
    if not client:
        return None
    try:
        result = client.table("transcriptions").select("*").eq("video_id", video_id).single().execute()
        return result.data
    except Exception:
        return None


def save_cache(video_id: str, transcript: str, summary: str | None, method: str) -> None:
    client = _get_client()
    if not client:
        return
    try:
        client.table("transcriptions").upsert({
            "video_id": video_id,
            "transcript": transcript,
            "summary": summary,
            "method": method,
        }).execute()
    except Exception:
        pass
