"""Rutas HTTP de la API del juego del ahorcado."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain import Game
from app.schemas import (
    CreateGameRequest,
    GameResponse,
    GuessRequest,
    GuessResponse,
    HealthResponse,
)
from app.service import GameNotFoundError, HangmanService, InvalidMoveError
from app.words import WORDS

router = APIRouter()


def get_service(request: Request) -> HangmanService:
    """Obtiene el servicio de juego asociado a la aplicación.

    Args:
        request: Petición HTTP actual.

    Returns:
        Servicio inicializado durante el arranque de FastAPI.
    """
    return request.app.state.game_service


def serialize_game(game: Game) -> dict[str, object]:
    """Convierte una entidad de dominio en una respuesta segura.

    La palabra secreta solo se incluye cuando la partida ha terminado.

    Args:
        game: Partida que se desea exponer.

    Returns:
        Diccionario compatible con :class:`GameResponse`.
    """
    return {
        "id": game.id,
        "category": game.category,
        "masked_word": game.masked_word,
        "guessed_letters": sorted(game.guessed_letters),
        "wrong_letters": sorted(game.wrong_letters),
        "attempts_left": game.attempts_left,
        "max_attempts": game.max_attempts,
        "status": game.status.value,
        "created_at": game.created_at,
        "updated_at": game.updated_at,
        "word": game.word if game.status.value != "playing" else None,
    }


@router.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health() -> dict[str, str]:
    """Confirma que el proceso de la API está disponible."""
    return {"status": "ok"}


@router.get("/api/v1/categories", tags=["Partidas"])
def categories() -> dict[str, list[str]]:
    """Lista las categorías de palabras disponibles."""
    return {"categories": sorted(WORDS)}


@router.post(
    "/api/v1/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Partidas"],
)
def create_game(
    payload: CreateGameRequest,
    service: HangmanService = Depends(get_service),
) -> dict[str, object]:
    """Crea y devuelve una nueva partida de ahorcado."""
    try:
        game = service.create_game(payload.category, payload.max_attempts)
        return serialize_game(game)
    except InvalidMoveError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/api/v1/games/{game_id}", response_model=GameResponse, tags=["Partidas"])
def get_game(
    game_id: str,
    service: HangmanService = Depends(get_service),
) -> dict[str, object]:
    """Devuelve el estado actual de una partida."""
    try:
        return serialize_game(service.get_game(game_id))
    except GameNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post(
    "/api/v1/games/{game_id}/guesses",
    response_model=GuessResponse,
    tags=["Partidas"],
)
def make_guess(
    game_id: str,
    payload: GuessRequest,
    service: HangmanService = Depends(get_service),
) -> dict[str, object]:
    """Procesa una letra o palabra y devuelve el nuevo estado."""
    try:
        result = service.guess(game_id, payload.guess)
        return {
            **serialize_game(result.game),
            "correct": result.correct,
            "message": result.message,
        }
    except GameNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except InvalidMoveError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


"""Rutas HTTP de la API del juego del ahorcado."""
