import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  server: {
    port: 5173,
    // Development only: the browser talks to Vite, which forwards /api to the
    // FastAPI dev server so no CORS negotiation is needed in day-to-day work.
    proxy: {
      '/api': {
        target: loadEnv(mode, process.cwd(), 'VITE_').VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}'],
    restoreMocks: true,
    unstubGlobals: true,
  },
}))
