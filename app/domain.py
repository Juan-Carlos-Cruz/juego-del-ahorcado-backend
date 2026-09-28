from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GameStatus(str, Enum):
    playing = "playing"
    won = "won"
    lost = "lost"


@dataclass
class Game:
    id: str
    word: str
    category: str
    max_attempts: int
    guessed_letters: set[str] = field(default_factory=set)
    wrong_letters: set[str] = field(default_factory=set)
    status: GameStatus = GameStatus.playing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def attempts_left(self) -> int:
        return self.max_attempts - len(self.wrong_letters)

    @property
    def masked_word(self) -> str:
        return " ".join(letter if not letter.isalpha() or letter in self.guessed_letters else "_" for letter in self.word)

    @property
    def is_complete(self) -> bool:
        return all(not letter.isalpha() or letter in self.guessed_letters for letter in self.word)

