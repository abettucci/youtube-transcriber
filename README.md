# YouTube Transcriber

Transcribe and summarize YouTube videos. FastAPI backend + Next.js frontend.

## How it works

1. Tries `youtube-transcript-api` first (fast, uses existing captions)
2. Falls back to `yt-dlp` + `openai-whisper` if no captions available (works on any video)
3. Caches results in Supabase to avoid reprocessing the same video

## Stack

- **Backend**: Python + FastAPI → Railway
- **Frontend**: Next.js → Vercel
- **Cache**: Supabase (Postgres)
- **Transcription**: youtube-transcript-api + Whisper
- **Summarization**: OpenAI gpt-4o-mini

---

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install ffmpeg (required for Whisper fallback)
brew install ffmpeg   # macOS

cp .env.example .env
# Edit .env with your keys

uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env.local
# Set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

npm run dev
# UI available at http://localhost:3000
```

---

## Deployment

### 1. Supabase (cache)

Create a free project at [supabase.com](https://supabase.com) and run:

```sql
CREATE TABLE transcriptions (
  video_id   TEXT PRIMARY KEY,
  transcript TEXT NOT NULL,
  summary    TEXT,
  method     TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Copy your project URL and anon key.

### 2. Railway (backend)

1. Push this repo to GitHub
2. Create new project in [railway.app](https://railway.app) → Deploy from GitHub repo
3. Set root directory to `backend/`
4. Add environment variables:
   ```
   OPENAI_API_KEY=sk-...
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_KEY=eyJ...
   ```

### 3. Vercel (frontend)

1. Import repo in [vercel.com](https://vercel.com)
2. Set root directory to `frontend/`
3. Add environment variable:
   ```
   NEXT_PUBLIC_BACKEND_URL=https://your-app.railway.app
   ```

---

## API

```
POST /transcript   { "url": "https://youtube.com/...", "lang": "es" }
POST /summary      { "url": "https://youtube.com/...", "lang": "es" }
GET  /health
```
