import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

/**
 * Serve static files and web UIs.
 * Call this after tRPC middleware is mounted.
 */
export function mountStaticRoutes(app: express.Application) {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const publicDir = path.resolve(__dirname, '../../public');

  function servePublicFile(filename: string, res: express.Response) {
    const filePath = path.join(publicDir, filename);
    if (fs.existsSync(filePath)) {
      res.sendFile(filePath);
    } else {
      const cwdPath = path.resolve(process.cwd(), 'public', filename);
      if (fs.existsSync(cwdPath)) {
        res.sendFile(cwdPath);
      } else {
        res.status(404).send(`UI not found. Searched: ${filePath} and ${cwdPath}`);
      }
    }
  }

  // /chat -> simple chat UI
  app.get('/chat', (_req, res) => servePublicFile('chat.html', res));

  // /nexus -> MIST Nexus command center dashboard
  app.get('/nexus', (_req, res) => servePublicFile('nexus.html', res));

  // / -> redirect to nexus (main entry point)
  app.get('/', (_req, res) => res.redirect('/nexus'));

  // Static assets
  app.use('/public', express.static(publicDir));
}
