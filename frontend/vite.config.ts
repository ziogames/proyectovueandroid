import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // permite acceso desde la red local
    port: 5173,
    proxy: {
      // Todas las llamadas a /api se redirigen al backend Django
      '/api': {
        target: 'http://192.168.1.48:8000', // IP de tu PC con Django
        changeOrigin: true,
        secure: false,
      },
    },
  },

})
