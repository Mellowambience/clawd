import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

/**
 * Serve static files and the /chat web UI.
 * Call this after tRPC middleware is mounted.
 */
export function mountStaticRoutes(app: express.Application) {
  // Resolve public dir relative to this file (server/_core/static.ts -> ../../public)
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const publicDir = path.resolve(__dirname, '../../public');
  const chatFile = path.join(publicDir, 'chat.html');

  // Serve /chat -> public/chat.html
  app.get('/chat', (_req, res) => {
    if (fs.existsSync(chatFile)) {
      res.sendFile(chatFile);
    } else {
      // Fallback: try cwd-based path
      const cwdPath = path.resolve(process.cwd(), 'public', 'chat.html');
      if (fs.existsSync(cwdPath)) {
        res.sendFile(cwdPath);
      } else {
        res.status(404).send('Chat UI not found. Searched: ' + chatFile + ' and ' + cwdPath);
      }
    }
  });

  // Serve any other static assets from public/
  app.use('/public', express.static(publicDir));
}
