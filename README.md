# Juego del Ahorcado API

Aplicación MVP con un backend en FastAPI y un frontend en React con Vite.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Juan-Carlos-Cruz/juego-del-ahorcado-backend)

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

El archivo `render.yaml` crea dos servicios mediante un mismo Blueprint:

- `juego-del-ahorcado-api`: API desarrollada con FastAPI.
- `juego-del-ahorcado-frontend`: sitio estático desarrollado con React.

Usa el botón **Deploy to Render**, inicia sesión y confirma la creación de ambos servicios. El frontend recibe la URL pública del backend mediante `VITE_API_URL`.

El plan gratuito usa SQLite en almacenamiento temporal; las partidas pueden reiniciarse al redesplegar o reiniciar la instancia. Para una versión posterior se recomienda PostgreSQL administrado.
