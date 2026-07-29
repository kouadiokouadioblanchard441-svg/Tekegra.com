import path from 'path';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

const rawPort = process.env.PORT;
const port = rawPort ? Number(rawPort) : 3000;

// BASE_PATH is injected by Replit in dev; default to '/' for Vercel / standalone builds
const basePath = process.env.BASE_PATH ?? '/';

const isReplit = process.env.REPL_ID !== undefined;
const isDev = process.env.NODE_ENV !== 'production';

export default defineConfig({
  base: basePath,
  plugins: [
    react(),
    tailwindcss(),
    // Replit-only plugins — skipped on Vercel / CI
    ...(isDev && isReplit
      ? [
          await import('@replit/vite-plugin-runtime-error-modal').then((m) =>
            m.default(),
          ),
          await import('@replit/vite-plugin-cartographer').then((m) =>
            m.cartographer({
              root: path.resolve(import.meta.dirname, '..'),
            }),
          ),
          await import('@replit/vite-plugin-dev-banner').then((m) =>
            m.devBanner(),
          ),
        ]
      : []),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, 'src'),
      // Workspace lib re-exported through the @/ alias so pages can import
      // from "@/lib/api-client-react/..." without duplicating generated code.
      '@/lib/api-client-react': path.resolve(import.meta.dirname, '../../lib/api-client-react'),
      '@assets': path.resolve(
        import.meta.dirname,
        '..',
        '..',
        'attached_assets',
      ),
    },
    dedupe: ['react', 'react-dom'],
  },
  root: path.resolve(import.meta.dirname),
  build: {
    // On Vercel (VERCEL=1), output directly to the project root's /public
    // so Vercel finds it without any copy step, regardless of dashboard settings.
    // Locally (Replit / CI), keep output inside dist/public.
    outDir: process.env.VERCEL
      ? path.resolve(import.meta.dirname, '../../public')
      : path.resolve(import.meta.dirname, 'dist/public'),
    emptyOutDir: true,
  },
  server: {
    port,
    strictPort: true,
    host: '0.0.0.0',
    allowedHosts: true,
    fs: {
      strict: true,
    },
  },
  preview: {
    port,
    host: '0.0.0.0',
    allowedHosts: true,
  },
});
