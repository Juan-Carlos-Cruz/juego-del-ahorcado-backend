"""Esquemas de entrada y salida expuestos por la API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CreateGameRequest(BaseModel):
    """Datos opcionales para crear una partida."""

    category: str | None = Field(default=None, examples=["tecnologia"])
    max_attempts: int = Field(default=6, ge=1, le=12)


class GuessRequest(BaseModel):
    """Jugada enviada por el usuario."""

    guess: str = Field(min_length=1, max_length=50, examples=["a"])

    @field_validator("guess")
    @classmethod
    def clean_guess(cls, value: str) -> str:
        """Limpia y valida una letra o palabra.

        Args:
            value: Texto enviado por el jugador.

        Returns:
            El texto sin espacios externos y en minúsculas.

        Raises:
            ValueError: Si contiene caracteres no permitidos.
        """
        cleaned = value.strip().lower()
        has_only_valid_characters = all(
            character.isalpha() or character in " -" for character in cleaned
        )
        if not cleaned or not has_only_valid_characters:
            raise ValueError("La jugada solo puede contener letras, espacios o guiones")
        return cleaned


class GameResponse(BaseModel):
    """Estado público de una partida."""

    id: str
    category: str
    masked_word: str
    guessed_letters: list[str]
    wrong_letters: list[str]
    attempts_left: int
    max_attempts: int
    status: Literal["playing", "won", "lost"]
    created_at: datetime
    updated_at: datetime
    word: str | None = None


class GuessResponse(GameResponse):
    """Resultado de una jugada junto con el nuevo estado."""

    correct: bool
    message: str


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: Literal["ok"]


"""Esquemas de entrada y salida expuestos por la API."""
