import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
export default defineConfig({
  base: './',
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        okna: resolve(__dirname, 'okna/index.html'),
        narva: resolve(__dirname, 'narva/index.html'),
      },
    },
  },
})
