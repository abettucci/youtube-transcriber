import re
import os
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import yt_dlp
import whisper


def extract_video_id(url: str) -> str:
    pattern = r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"URL inválida: {url}")
    return match.group(1)


def _parse_transcript(entries: list) -> str:
    return " ".join(e["text"].replace("\n", " ").strip() for e in entries if e.get("text"))


def get_transcript(video_id: str, lang: str = "es") -> dict:
    # 1. Try youtube-transcript-api (fast, no download)
    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, "es", "en"])
        text = _parse_transcript(entries)
        if text.strip():
            return {"text": text, "method": "captions", "word_count": len(text.split())}
    except (NoTranscriptFound, TranscriptsDisabled):
        pass

    # 2. Fallback: yt-dlp + Whisper
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = _download_audio(video_id, tmpdir)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=lang if lang != "es" else None)
        text = result["text"].strip()

    return {"text": text, "method": "whisper", "word_count": len(text.split())}


def _download_audio(video_id: str, output_dir: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join(output_dir, "audio.mp3")
