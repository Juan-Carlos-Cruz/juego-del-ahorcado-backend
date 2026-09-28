"""Entidades y reglas básicas del dominio del juego."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GameStatus(str, Enum):
    """Estados posibles de una partida."""

    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class Game:
    """Representa una partida de ahorcado.

    Attributes:
        id: Identificador único de la partida.
        word: Palabra secreta normalizada.
        category: Categoría a la que pertenece la palabra.
        max_attempts: Cantidad máxima de jugadas incorrectas.
        guessed_letters: Letras acertadas por el jugador.
        wrong_letters: Letras o palabras fallidas.
        status: Estado actual de la partida.
        created_at: Fecha de creación en UTC.
        updated_at: Fecha de la última jugada en UTC.
    """

    id: str
    word: str
    category: str
    max_attempts: int
    guessed_letters: set[str] = field(default_factory=set)
    wrong_letters: set[str] = field(default_factory=set)
    status: GameStatus = GameStatus.PLAYING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def attempts_left(self) -> int:
        """Calcula la cantidad de intentos disponibles."""
        return self.max_attempts - len(self.wrong_letters)

    @property
    def masked_word(self) -> str:
        """Construye la palabra visible sin revelar letras pendientes."""
        visible_characters = (
            letter if not letter.isalpha() or letter in self.guessed_letters else "_"
            for letter in self.word
        )
        return " ".join(visible_characters)

    @property
    def is_complete(self) -> bool:
        """Indica si el jugador encontró todas las letras de la palabra."""
        return all(
            not letter.isalpha() or letter in self.guessed_letters
            for letter in self.word
        )
