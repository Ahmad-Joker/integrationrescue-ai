import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const backend = process.env.IR_BACKEND_URL ?? 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: { '/api': backend, '/sim': backend },
  },
})
