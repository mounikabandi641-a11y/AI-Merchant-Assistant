from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.assistant import router as assistant_router
from app.api.routes.disputes import api_router as api_disputes_router
from app.api.routes.disputes import router as disputes_router
from app.api.routes.fraud import router as fraud_router
from app.api.routes.transactions import router as transactions_router
from app.db.database import create_db_and_tables
from app.services.ml_service import load_model

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

app = FastAPI(
    title="AI Merchant Assistant API",
    description="Backend for dispute and fraud resolution for merchant transactions.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    create_db_and_tables()
    app.state.risk_model = load_model()


app.include_router(transactions_router)
app.include_router(disputes_router)
app.include_router(api_disputes_router)
app.include_router(fraud_router)
app.include_router(assistant_router)


@app.get("/", response_model=None)
def read_root() -> FileResponse | dict[str, str]:
    if FRONTEND_INDEX.is_file():
        return FileResponse(FRONTEND_INDEX)
    return {"message": "AI Merchant Assistant backend is running."}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
