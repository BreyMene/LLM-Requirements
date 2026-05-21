import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/analyze': 'http://localhost:8000',
      '/generate': 'http://localhost:8000',
      '/train': 'http://localhost:8000'
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: true,
    sourcemap: false
  }
});
