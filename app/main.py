"""Punto de entrada y configuración principal de FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import settings
from app.repository import GameRepository
from app.service import HangmanService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa las dependencias compartidas de la aplicación.

    Args:
        app: Instancia de FastAPI que está iniciando.

    Yields:
        El control a FastAPI mientras la aplicación está activa.
    """
    app.state.game_service = HangmanService(GameRepository(settings.database_path))
    yield


app = FastAPI(
    title=settings.app_name,
    description="API REST para jugar al ahorcado desde cualquier frontend.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allowed_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Informa dónde se encuentra la documentación interactiva."""
    return {"message": "Juego del Ahorcado API", "docs": "/docs"}


"""Punto de entrada y configuración principal de FastAPI."""
