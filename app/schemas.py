from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CreateGameRequest(BaseModel):
    category: str | None = Field(default=None, examples=["tecnologia"])
    max_attempts: int = Field(default=6, ge=1, le=12)


class GuessRequest(BaseModel):
    guess: str = Field(min_length=1, max_length=50, examples=["a"])

    @field_validator("guess")
    @classmethod
    def clean_guess(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned or not all(character.isalpha() or character in " -" for character in cleaned):
            raise ValueError("La jugada solo puede contener letras, espacios o guiones")
        return cleaned


class GameResponse(BaseModel):
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
    correct: bool
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"]

