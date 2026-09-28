import os
from pathlib import Path

os.environ["DATABASE_PATH"] = str(Path(__file__).parent / "test_hangman.db")

from fastapi.testclient import TestClient

from app.main import app


def test_game_flow() -> None:
    with TestClient(app) as client:
        created = client.post("/api/v1/games", json={"category": "tecnologia", "max_attempts": 6})
        assert created.status_code == 201
        game = created.json()
        assert game["status"] == "playing"
        assert game["word"] is None
        assert "_" in game["masked_word"]

        guessed = client.post(f"/api/v1/games/{game['id']}/guesses", json={"guess": "x"})
        assert guessed.status_code == 200
        assert guessed.json()["correct"] is False
        assert guessed.json()["attempts_left"] == 5


def test_unknown_category() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/games", json={"category": "inexistente"})
        assert response.status_code == 422


def test_missing_game() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/games/no-existe")
        assert response.status_code == 404
