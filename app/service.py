"""Casos de uso y reglas de negocio del juego del ahorcado."""

import random
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.domain import Game, GameStatus
from app.repository import GameRepository
from app.words import WORDS


class GameNotFoundError(Exception):
    """Indica que no existe una partida con el identificador solicitado."""


class InvalidMoveError(Exception):
    """Indica que una jugada no es válida para el estado actual."""


@dataclass(frozen=True)
class GuessResult:
    """Resultado producido al procesar una jugada.

    Attributes:
        game: Estado actualizado de la partida.
        correct: Indica si la letra o palabra fue acertada.
        message: Mensaje corto para mostrar al jugador.
    """

    game: Game
    correct: bool
    message: str


def normalize(value: str) -> str:
    """Convierte texto a minúsculas y elimina marcas diacríticas.

    Args:
        value: Texto que se desea normalizar.

    Returns:
        Texto comparable sin tildes ni diferencias entre mayúsculas.
    """
    decomposed_value = unicodedata.normalize("NFD", value.lower())
    return "".join(
        character
        for character in decomposed_value
        if unicodedata.category(character) != "Mn"
    )


class HangmanService:
    """Coordina la creación, consulta y actualización de partidas.

    Args:
        repository: Repositorio utilizado para persistir las partidas.
    """

    def __init__(self, repository: GameRepository) -> None:
        """Inicializa el servicio con su dependencia de persistencia.

        Args:
            repository: Repositorio utilizado para persistir las partidas.
        """
        self.repository = repository

    def create_game(self, category: str | None, max_attempts: int) -> Game:
        """Crea una partida con una palabra seleccionada al azar.

        Args:
            category: Categoría solicitada o ``None`` para elegir una al azar.
            max_attempts: Número máximo de errores permitidos.

        Returns:
            La partida creada y persistida.

        Raises:
            InvalidMoveError: Si la categoría solicitada no existe.
        """
        selected_category = self._select_category(category)
        word = normalize(random.choice(WORDS[selected_category]))
        game = Game(
            id=str(uuid4()),
            word=word,
            category=selected_category,
            max_attempts=max_attempts,
        )
        self.repository.save(game)
        return game

    def _select_category(self, category: str | None) -> str:
        """Valida la categoría o selecciona una al azar."""
        selected_category = (
            category.lower().strip() if category else random.choice(list(WORDS))
        )
        if selected_category not in WORDS:
            available = ", ".join(sorted(WORDS))
            raise InvalidMoveError(f"Categoría no válida. Disponibles: {available}")
        return selected_category

    def get_game(self, game_id: str) -> Game:
        """Obtiene una partida existente.

        Args:
            game_id: Identificador único de la partida.

        Returns:
            La partida solicitada.

        Raises:
            GameNotFoundError: Si la partida no existe.
        """
        game = self.repository.get(game_id)
        if game is None:
            raise GameNotFoundError("Partida no encontrada")
        return game

    def guess(self, game_id: str, raw_guess: str) -> GuessResult:
        """Procesa el intento de adivinar una letra o palabra.

        Args:
            game_id: Identificador de la partida.
            raw_guess: Letra o palabra enviada por el jugador.

        Returns:
            Resultado de la jugada y estado actualizado de la partida.

        Raises:
            GameNotFoundError: Si la partida no existe.
            InvalidMoveError: Si la partida terminó o la letra está repetida.
        """
        game = self.get_game(game_id)
        if game.status is not GameStatus.PLAYING:
            raise InvalidMoveError("La partida ya terminó")

        guess = normalize(raw_guess.strip())
        if len(guess) == 1:
            correct, message = self._guess_letter(game, guess)
        else:
            correct, message = self._guess_word(game, guess)

        if game.is_complete:
            game.status = GameStatus.WON
        elif game.attempts_left <= 0:
            game.status = GameStatus.LOST
        game.updated_at = datetime.now(timezone.utc)
        self.repository.save(game)
        return GuessResult(game=game, correct=correct, message=message)

    @staticmethod
    def _guess_letter(game: Game, letter: str) -> tuple[bool, str]:
        """Aplica a la partida un intento de una sola letra."""
        used_letters = game.guessed_letters | game.wrong_letters
        if letter in used_letters:
            raise InvalidMoveError("Esa letra ya fue utilizada")

        is_correct = letter in game.word
        target_collection = game.guessed_letters if is_correct else game.wrong_letters
        target_collection.add(letter)
        message = "¡Letra correcta!" if is_correct else "La letra no está en la palabra"
        return is_correct, message

    @staticmethod
    def _guess_word(game: Game, word: str) -> tuple[bool, str]:
        """Aplica a la partida un intento de palabra completa."""
        is_correct = word == game.word
        if is_correct:
            game.guessed_letters.update(
                letter for letter in game.word if letter.isalpha()
            )
            return True, "¡Adivinaste la palabra!"

        game.wrong_letters.add(word)
        return False, "La palabra no es correcta"
