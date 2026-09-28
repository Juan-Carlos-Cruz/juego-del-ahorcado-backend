"""Configuración de la aplicación obtenida desde variables de entorno."""

import os
from dataclasses import dataclass

DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:5173"


@dataclass(frozen=True)
class Settings:
    """Agrupa la configuración necesaria para ejecutar la API.

    Attributes:
        app_name: Nombre mostrado en la documentación OpenAPI.
        database_path: Ruta del archivo SQLite.
        allowed_origins_raw: Orígenes CORS separados por comas.
    """

    app_name: str = os.getenv("APP_NAME", "Juego del Ahorcado API")
    database_path: str = os.getenv("DATABASE_PATH", "hangman.db")
    allowed_origins_raw: str = os.getenv(
        "ALLOWED_ORIGINS",
        DEFAULT_ALLOWED_ORIGINS,
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Devuelve los orígenes CORS como una lista limpia."""
        origins = self.allowed_origins_raw.split(",")
        return [origin.strip() for origin in origins if origin.strip()]


settings = Settings()
