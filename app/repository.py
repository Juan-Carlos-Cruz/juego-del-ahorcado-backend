import json
import sqlite3
from datetime import datetime
from threading import Lock

from app.domain import Game, GameStatus


class GameRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._lock = Lock()
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    word TEXT NOT NULL,
                    category TEXT NOT NULL,
                    max_attempts INTEGER NOT NULL,
                    guessed_letters TEXT NOT NULL,
                    wrong_letters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save(self, game: Game) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    guessed_letters=excluded.guessed_letters,
                    wrong_letters=excluded.wrong_letters,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    game.id,
                    game.word,
                    game.category,
                    game.max_attempts,
                    json.dumps(sorted(game.guessed_letters)),
                    json.dumps(sorted(game.wrong_letters)),
                    game.status.value,
                    game.created_at.isoformat(),
                    game.updated_at.isoformat(),
                ),
            )

    def get(self, game_id: str) -> Game | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
        if row is None:
            return None
        return Game(
            id=row["id"],
            word=row["word"],
            category=row["category"],
            max_attempts=row["max_attempts"],
            guessed_letters=set(json.loads(row["guessed_letters"])),
            wrong_letters=set(json.loads(row["wrong_letters"])),
            status=GameStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

