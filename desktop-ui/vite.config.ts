import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    base: './', // Just in case for electron relative paths
    server: {
        port: 5173,
        strictPort: true,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
            },
            '/health': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
            },
            '/openapi': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
            },
            '/swagger-ui': {
                target: 'http://127.0.0.1:5001',
                changeOrigin: true,
            },
        }
    },
});
