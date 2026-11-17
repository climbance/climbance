import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'

// the API on the pages' origin, so no request crosses to another one
const api = { '/api': 'http://127.0.0.1:8000' }

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // the build an error report names, since every web build is version 0.0.0
  define: { __BUILT__: JSON.stringify(new Date().toISOString().slice(0, 16)) },
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: { proxy: api },
  preview: { proxy: api },
})
