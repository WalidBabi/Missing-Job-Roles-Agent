import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
  },
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify('http://13.62.19.27:8000/api')
  }
})

