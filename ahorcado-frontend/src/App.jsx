import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [juegoId, setJuegoId] = useState(null)
  const [palabraOculta, setPalabraOculta] = useState([])
  const [intentosRestantes, setIntentosRestantes] = useState(6)
  const [estadoJuego, setEstadoJuego] = useState('inactive') 
  const [mensaje, setMensaje] = useState('')

  const abecedario = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".split("")

  // Función para iniciar un nuevo juego
  const iniciarJuego = async () => {
    try {
      // Usamos la ruta y el body dictados por Swagger UI
      const response = await fetch(`${API_URL}/api/v1/games`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: "tecnologia", // Puedes cambiar esto para que el usuario lo seleccione
          max_attempts: 6
        })
      })

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      setJuegoId(data.id)
      // Convertimos el string 'masked_word' a un array de letras para poder iterarlo
      setPalabraOculta(data.masked_word ? data.masked_word.split('') : []) 
      setIntentosRestantes(data.attempts_left)
      setEstadoJuego(data.status) // El backend devuelve "playing", etc.
      setMensaje('')
    } catch (error) {
      console.error("Error al conectar con el backend:", error)
      setMensaje("Error al conectar con el servidor.")
    }
  }

  // Función para adivinar una letra
  const adivinarLetra = async (letra) => {
    if (estadoJuego !== 'playing') return

    try {
      // Usamos la ruta de guesses de Swagger UI
      const response = await fetch(`${API_URL}/api/v1/games/${juegoId}/guesses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Asumiendo que el request body para enviar la letra es 'letter'
        body: JSON.stringify({ letter: letra.toLowerCase() }) 
      })
      
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`)
      }

      const data = await response.json()
      
      setPalabraOculta(data.masked_word ? data.masked_word.split('') : [])
      setIntentosRestantes(data.attempts_left)
      setEstadoJuego(data.status) 
      
      if (data.detail) {
        setMensaje(data.detail)
      }
    } catch (error) {
      console.error("Error al enviar la letra:", error)
    }
  }

  return (
    <div className="App">
      <h1>Juego del Ahorcado</h1>
      
      {estadoJuego === 'inactive' ? (
        <button onClick={iniciarJuego} className="btn-iniciar">
          Comenzar Juego
        </button>
      ) : (
        <div className="juego-contenedor">
          <div className="info-juego">
            <p>Intentos restantes: <strong>{intentosRestantes}</strong></p>
            <h2 className="palabra">
              {palabraOculta.map((caracter, index) => (
                <span key={index} className="letra-espacio">
                  {caracter}
                </span>
              ))}
            </h2>
          </div>

          <div className="teclado">
            {abecedario.map((letra) => (
              <button 
                key={letra} 
                onClick={() => adivinarLetra(letra)}
                disabled={estadoJuego !== 'playing'}
              >
                {letra}
              </button>
            ))}
          </div>

          {mensaje && <p className="mensaje">{mensaje}</p>}

          {(estadoJuego === 'won' || estadoJuego === 'lost') && (
            <div className="resultado">
              <h3>{estadoJuego === 'won' ? '¡Felicidades, ganaste!' : 'Fin del juego, perdiste.'}</h3>
              <button onClick={iniciarJuego}>Jugar de nuevo</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App