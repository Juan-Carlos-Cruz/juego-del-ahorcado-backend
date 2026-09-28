import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // La API solo acepta CORS desde http://localhost:5173 (ver app/main.py).
    // Se fija el puerto para que Vite no salte a otro y la conexión falle.
    port: 5173,
    strictPort: true,
  },
})
