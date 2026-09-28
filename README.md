# Juego del Ahorcado API

Backend MVP construido con FastAPI para ser consumido por un frontend web o móvil.

## Funcionalidades

- Crear una partida con categoría aleatoria o elegida.
- Adivinar una letra o la palabra completa.
- Consultar el estado de una partida.
- Control de intentos, victoria y derrota.
- La palabra secreta solo se revela cuando termina la partida.
- Persistencia ligera con SQLite y CORS configurable.
- Documentación interactiva OpenAPI en `/docs`.

## Ejecutar localmente

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Abre `http://localhost:8000/docs`.

## API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `GET` | `/api/v1/categories` | Categorías disponibles |
| `POST` | `/api/v1/games` | Crear una partida |
| `GET` | `/api/v1/games/{id}` | Consultar una partida |
| `POST` | `/api/v1/games/{id}/guesses` | Enviar letra o palabra |

Crear una partida:

```bash
curl -X POST http://localhost:8000/api/v1/games \
  -H 'Content-Type: application/json' \
  -d '{"category":"tecnologia","max_attempts":6}'
```

Enviar una jugada:

```bash
curl -X POST http://localhost:8000/api/v1/games/ID/guesses \
  -H 'Content-Type: application/json' \
  -d '{"guess":"a"}'
```

Ejemplo desde el frontend:

```js
const response = await fetch(`${API_URL}/api/v1/games`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ category: "tecnologia", max_attempts: 6 }),
});
const game = await response.json();
```

## Pruebas

```bash
pytest -q
```

## Despliegue en Render

El archivo `render.yaml` permite crear el servicio como Blueprint. Conecta este repositorio en Render y el servicio se configura automáticamente. En producción cambia `ALLOWED_ORIGINS` por la URL exacta del frontend.

El plan gratuito usa SQLite en almacenamiento temporal; las partidas pueden reiniciarse al redesplegar o reiniciar la instancia. Para una versión posterior se recomienda PostgreSQL administrado.
