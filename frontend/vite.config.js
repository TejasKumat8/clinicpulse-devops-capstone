import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Development: `npm run dev` proxies /api calls to locally running FastAPI (port 8000).
// Production / Docker: relative /api requests are routed by Nginx reverse proxy or Kubernetes Ingress.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
