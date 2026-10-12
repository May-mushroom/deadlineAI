import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Build output goes to dist/. The manifest.json and background.js live in
// public/ so Vite copies them into dist/ unchanged during the build.
// Load the dist/ folder as an "unpacked extension" in chrome://extensions.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
