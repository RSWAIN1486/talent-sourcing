import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  preview: {
    host: "0.0.0.0",
    port: Number(process.env.PORT) || 4173,
    allowedHosts: ["talent-sourcing-zerograd-fe.onrender.com"], // 👈 Add this
  },
  server: {
    host: "0.0.0.0",
    port: Number(process.env.PORT) || 4173,
  }
})
