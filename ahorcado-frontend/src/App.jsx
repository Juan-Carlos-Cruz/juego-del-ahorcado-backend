import { useState } from 'react'
import './App.css'

const API_URL = (
  import.meta.env.VITE_API_URL ?? 'https://juego-del-ahorcado-api.onrender.com'
).replace(/\/$/, '')

const CATEGORIA = 'tecnologia'
const MAX_INTENTOS = 6
const abecedario = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'.split('')

/**
 * Lee el mensaje de error que devuelve FastAPI.
 *
 * `detail` es un texto en los errores de negocio (404, 409) y una lista de
 * errores de validación en los 422.
 */
function leerDetalle(payload) {
  const detail = payload?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((error) => error?.msg).filter(Boolean).join('. ') || null
  }
  return null
}

/**
 * Convierte la respuesta del backend en el estado que consume la interfaz.
 *
 * `masked_word` llega separado por espacios ("_ _ A _"), por lo que se divide
 * por espacios y no carácter por carácter.
 */
function aPartida(data) {
  return {
    id: data.id,
    estado: data.status,
    casillas: data.masked_word ? data.masked_word.split(' ') : [],
    categoria: data.category,
    intentosRestantes: data.attempts_left,
    maxIntentos: data.max_attempts,
    aciertos: data.guessed_letters ?? [],
    fallos: data.wrong_letters ?? [],
    palabra: data.word,
  }
}

function App() {
  const [partida, setPartida] = useState(null)
  const [mensaje, setMensaje] = useState(null)
  const [cargando, setCargando] = useState(false)

  const letrasUsadas = new Set(
    partida ? [...partida.aciertos, ...partida.fallos] : [],
  )

  // Un fallo de red no trae mensaje útil: se explica qué revisar.
  const textoDeError = (error, accion) =>
    error instanceof TypeError
      ? `No se pudo conectar con la API en ${API_URL}. Verifica que el servidor esté en ejecución.`
      : `No se pudo ${accion}: ${error.message}`

  // Función para iniciar un nuevo juego
  const iniciarJuego = async () => {
    setCargando(true)
    setMensaje(null)
    try {
      const response = await fetch(`${API_URL}/api/v1/games`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: CATEGORIA,
          max_attempts: MAX_INTENTOS,
        }),
      })

      // El cuerpo se lee siempre: los errores de FastAPI traen `detail`.
      const data = await response.json().catch(() => null)
      if (!response.ok) {
        throw new Error(leerDetalle(data) ?? `la API respondió ${response.status}`)
      }

      setPartida(aPartida(data))
    } catch (error) {
      console.error('Error al iniciar la partida:', error)
      setPartida(null)
      setMensaje({ tipo: 'error', texto: textoDeError(error, 'iniciar la partida') })
    } finally {
      setCargando(false)
    }
  }

  // Función para adivinar una letra
  const adivinarLetra = async (letra) => {
    if (!partida || partida.estado !== 'playing' || cargando) return

    setCargando(true)
    try {
      const response = await fetch(
        `${API_URL}/api/v1/games/${partida.id}/guesses`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // El backend espera el campo `guess` (ver app/schemas.py).
          body: JSON.stringify({ guess: letra.toLowerCase() }),
        },
      )

      const data = await response.json().catch(() => null)
      if (!response.ok) {
        throw new Error(leerDetalle(data) ?? `la API respondió ${response.status}`)
      }

      setPartida(aPartida(data))
      // El backend informa el resultado en `message`, no en `detail`.
      setMensaje({
        tipo: data.correct ? 'acierto' : 'fallo',
        texto: data.message,
      })
    } catch (error) {
      console.error('Error al enviar la letra:', error)
      setMensaje({
        tipo: 'error',
        texto: textoDeError(error, 'registrar la letra'),
      })
    } finally {
      setCargando(false)
    }
  }

  if (!partida) {
    return (
      <div className="App">
        <h1>Juego del Ahorcado</h1>
        <p className="ayuda">
          Adivina la palabra oculta letra por letra. Se pierde al acumular{' '}
          {MAX_INTENTOS} letras equivocadas.
        </p>
        <button
          type="button"
          onClick={iniciarJuego}
          className="btn-iniciar"
          disabled={cargando}
        >
          {cargando ? 'Iniciando…' : 'Comenzar Juego'}
        </button>
        {mensaje && (
          <p className={`mensaje mensaje-${mensaje.tipo}`} role="alert">
            {mensaje.texto}
          </p>
        )}
      </div>
    )
  }

  const terminado = partida.estado !== 'playing'

  return (
    <div className="App">
      <h1>Juego del Ahorcado</h1>

      <div className="juego-contenedor">
        <div className="info-juego">
          <p className="categoria">Categoría: {partida.categoria}</p>
          <p>
            Intentos restantes:{' '}
            <strong>
              {partida.intentosRestantes} de {partida.maxIntentos}
            </strong>
          </p>
        </div>

        <h2 className="palabra">
          {partida.casillas.map((caracter, index) => (
            <span
              key={index}
              className={caracter === '_' ? 'letra letra-oculta' : 'letra'}
            >
              {caracter}
            </span>
          ))}
        </h2>

        <div className="teclado">
          {abecedario.map((letra) => {
            const usada = letrasUsadas.has(letra.toLowerCase())
            const acertada = partida.aciertos.includes(letra.toLowerCase())
            const clase = acertada
              ? 'tecla tecla-acierto'
              : usada
                ? 'tecla tecla-fallo'
                : 'tecla'

            return (
              <button
                type="button"
                key={letra}
                className={clase}
                onClick={() => adivinarLetra(letra)}
                disabled={usada || terminado || cargando}
                aria-label={
                  usada ? `${letra}: ya utilizada` : `Probar la letra ${letra}`
                }
              >
                {letra}
              </button>
            )
          })}
        </div>

        {mensaje && (
          <p
            className={`mensaje mensaje-${mensaje.tipo}`}
            role="status"
            aria-live="polite"
          >
            {mensaje.texto}
          </p>
        )}

        {terminado && (
          <div className="resultado">
            <h3>
              {partida.estado === 'won'
                ? '¡Felicidades, ganaste!'
                : 'Fin del juego, perdiste.'}
            </h3>
            {partida.palabra && (
              <p className="palabra-final">
                La palabra era <strong>{partida.palabra}</strong>
              </p>
            )}
            <button
              type="button"
              className="btn-iniciar"
              onClick={iniciarJuego}
              disabled={cargando}
            >
              {cargando ? 'Iniciando…' : 'Jugar de nuevo'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
