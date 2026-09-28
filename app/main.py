from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import settings
from app.repository import GameRepository
from app.service import HangmanService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.game_service = HangmanService(GameRepository(settings.database_path))
    yield


app = FastAPI(
    title=settings.app_name,
    description="API REST para jugar al ahorcado desde cualquier frontend.",
    version="1.0.0",
    lifespan=lifespan,
) 

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # El puerto de tu app React (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Juego del Ahorcado API", "docs": "/docs"}

