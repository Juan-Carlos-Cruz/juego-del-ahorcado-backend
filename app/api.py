from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain import Game
from app.schemas import CreateGameRequest, GameResponse, GuessRequest, GuessResponse, HealthResponse
from app.service import GameNotFoundError, HangmanService, InvalidMoveError

router = APIRouter()


def get_service(request: Request) -> HangmanService:
    return request.app.state.game_service


def serialize_game(game: Game) -> dict:
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
    return {"status": "ok"}


@router.get("/api/v1/categories", tags=["Partidas"])
def categories() -> dict[str, list[str]]:
    from app.words import WORDS
    return {"categories": sorted(WORDS)}


@router.post("/api/v1/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED, tags=["Partidas"])
def create_game(payload: CreateGameRequest, service: HangmanService = Depends(get_service)) -> dict:
    try:
        return serialize_game(service.create_game(payload.category, payload.max_attempts))
    except InvalidMoveError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/api/v1/games/{game_id}", response_model=GameResponse, tags=["Partidas"])
def get_game(game_id: str, service: HangmanService = Depends(get_service)) -> dict:
    try:
        return serialize_game(service.get_game(game_id))
    except GameNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/api/v1/games/{game_id}/guesses", response_model=GuessResponse, tags=["Partidas"])
def make_guess(game_id: str, payload: GuessRequest, service: HangmanService = Depends(get_service)) -> dict:
    try:
        game, correct, message = service.guess(game_id, payload.guess)
        return {**serialize_game(game), "correct": correct, "message": message}
    except GameNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except InvalidMoveError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

