'use strict';

/**
 * Planning Queue Dashboard
 * ------------------------
 * Serves the single-page front end used to enqueue tasks and watch the queue.
 *
 * The dashboard holds no business logic: it calls `/api/task` and
 * `/api/queue`, which the platform gateway routes to intake-service and
 * queue-collector.
 */

const path = require('node:path');
const express = require('express');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const SERVICE_NAME = 'queue-dashboard';

const PORT = Number(process.env.PORT || 8080);
const PUBLIC_DIR = path.join(__dirname, 'public');
const INDEX_FILE = path.join(PUBLIC_DIR, 'index.html');
const SHUTDOWN_TIMEOUT_MS = 10_000;

// ---------------------------------------------------------------------------
// HTTP application
// ---------------------------------------------------------------------------

const app = express();
app.disable('x-powered-by');

/** Liveness probe. */
app.get('/health', (_req, res) => res.json({ ok: true, service: SERVICE_NAME }));

app.use(express.static(PUBLIC_DIR));

// Single-page fallback: any other page request renders the app shell.
app.use((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  res.sendFile(INDEX_FILE);
});

// ---------------------------------------------------------------------------
// Start-up and shutdown
// ---------------------------------------------------------------------------

const server = app.listen(PORT, () => {
  console.log(`[${SERVICE_NAME}] listening on port ${PORT}`);
});

/**
 * Stops accepting connections and exits once open requests have finished.
 *
 * @param {string} signal The signal that triggered the shutdown.
 */
function shutdown(signal) {
  console.log(`[${SERVICE_NAME}] ${signal} received, shutting down`);

  // Fail-safe: never hang forever waiting for in-flight requests to finish.
  setTimeout(() => process.exit(1), SHUTDOWN_TIMEOUT_MS).unref();

  server.close(() => process.exit(0));
}

for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => shutdown(signal));
}
