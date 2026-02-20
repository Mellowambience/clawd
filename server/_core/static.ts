import express from 'express';
import path from 'path';

/**
 * Serve static files and the /chat web UI.
 * Call this after tRPC middleware is mounted.
 */
export function mountStaticRoutes(app: express.Application) {
  // Serve /chat → public/chat.html
  app.get('/chat', (_req, res) => {
    res.sendFile(path.resolve(process.cwd(), 'public', 'chat.html'));
  });

  // Serve any other static assets from public/
  app.use('/public', express.static(path.resolve(process.cwd(), 'public')));
}
