from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import transcript, summary

app = FastAPI(title="YouTube Transcriber", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcript.router)
app.include_router(summary.router)


@app.get("/health")
def health():
    return {"status": "ok"}
