import random
import unicodedata
from datetime import datetime, timezone
from uuid import uuid4

from app.domain import Game, GameStatus
from app.repository import GameRepository
from app.words import WORDS


class GameNotFoundError(Exception):
    pass


class InvalidMoveError(Exception):
    pass


def normalize(value: str) -> str:
    return "".join(character for character in unicodedata.normalize("NFD", value.lower()) if unicodedata.category(character) != "Mn")


class HangmanService:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    def create_game(self, category: str | None, max_attempts: int) -> Game:
        selected_category = category.lower().strip() if category else random.choice(list(WORDS))
        if selected_category not in WORDS:
            available = ", ".join(sorted(WORDS))
            raise InvalidMoveError(f"Categoría no válida. Disponibles: {available}")
        word = normalize(random.choice(WORDS[selected_category]))
        game = Game(id=str(uuid4()), word=word, category=selected_category, max_attempts=max_attempts)
        self.repository.save(game)
        return game

    def get_game(self, game_id: str) -> Game:
        game = self.repository.get(game_id)
        if game is None:
            raise GameNotFoundError("Partida no encontrada")
        return game

    def guess(self, game_id: str, raw_guess: str) -> tuple[Game, bool, str]:
        game = self.get_game(game_id)
        if game.status is not GameStatus.playing:
            raise InvalidMoveError("La partida ya terminó")

        guess = normalize(raw_guess.strip())
        if len(guess) == 1:
            if guess in game.guessed_letters or guess in game.wrong_letters:
                raise InvalidMoveError("Esa letra ya fue utilizada")
            correct = guess in game.word
            (game.guessed_letters if correct else game.wrong_letters).add(guess)
            message = "¡Letra correcta!" if correct else "La letra no está en la palabra"
        else:
            correct = guess == game.word
            if correct:
                game.guessed_letters.update(letter for letter in game.word if letter.isalpha())
                message = "¡Adivinaste la palabra!"
            else:
                game.wrong_letters.add(guess)
                message = "La palabra no es correcta"

        if game.is_complete:
            game.status = GameStatus.won
        elif game.attempts_left <= 0:
            game.status = GameStatus.lost
        game.updated_at = datetime.now(timezone.utc)
        self.repository.save(game)
        return game, correct, message

