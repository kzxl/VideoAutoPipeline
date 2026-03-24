import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5050',
      '/output': 'http://localhost:5050',
      '/static': 'http://localhost:5050',
    },
  },
  build: {
    outDir: 'dist',
  },
})
