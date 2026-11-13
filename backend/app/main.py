import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles

from backend.app.text_processor import MAX_TEXT_LENGTH, process_text_demo


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DEFAULT_FRONTEND_ORIGINS = (
    "http://localhost:5500,http://127.0.0.1:5500,"
    "http://localhost:5501,http://127.0.0.1:5501"
)

frontend_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGINS", DEFAULT_FRONTEND_ORIGINS).split(",")
    if origin.strip()
]

app = FastAPI(title="AI Smart Document Simplifier", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class SimplifyTextRequest(BaseModel):
    text: str = Field(max_length=MAX_TEXT_LENGTH)


class SimplifyTextResponse(BaseModel):
    result_text: str
    processor: str
    ai_configured: bool
    notice: str


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/simplify-text",
    response_model=SimplifyTextResponse,
    tags=["simplification"],
)
def simplify_text(request: SimplifyTextRequest) -> SimplifyTextResponse:
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    return process_text_demo(request.text)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
