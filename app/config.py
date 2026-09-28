import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Juego del Ahorcado API")
    database_path: str = os.getenv("DATABASE_PATH", "hangman.db")
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


settings = Settings()

