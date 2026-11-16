#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🧠 Installing runtime stream intelligence patch..."

mkdir -p .cache
mkdir -p tests

cat > tests/runtime-stream-intelligence.js << 'JSEOF'
const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(process.cwd(), '.cache');
const STREAM_CACHE = path.join(CACHE_DIR, 'stream-intelligence.json');

function save(obj) {
  fs.writeFileSync(STREAM_CACHE, JSON.stringify(obj, null, 2));
}

async function install(page) {
  await page.evaluateOnNewDocument(() => {

    window.__dsStreams = [];
    window.__dsFetches = [];
    window.__dsEndpoints = {};
    window.__dsCompletions = [];
    window.__dsUploads = [];

    const originalFetch = window.fetch;

    window.fetch = async (...args) => {
      const [url, opts] = args;

      try {
        window.__dsFetches.push({
          url,
          method: opts?.method || 'GET',
          ts: Date.now()
        });

        window.__dsEndpoints[url] = {
          method: opts?.method || 'GET',
          lastSeen: Date.now()
        };

      } catch {}

      const response = await originalFetch(...args);

      try {

        const cloned = response.clone();

        const ct = cloned.headers.get('content-type') || '';

        if (
          url.includes('/chat/completion') ||
          ct.includes('event-stream') ||
          ct.includes('stream')
        ) {

          const reader = cloned.body.getReader();
          const decoder = new TextDecoder();

          let full = '';

          async function pump() {
            while (true) {
              const { done, value } = await reader.read();

              if (done) break;

              const chunk = decoder.decode(value, { stream: true });

              full += chunk;

              window.__dsStreams.push({
                url,
                chunk,
                ts: Date.now()
              });

              const matches = chunk.match(/data:(.*)/g);

              if (matches) {
                for (const m of matches) {
                  try {
                    const cleaned = m.replace(/^data:/, '').trim();

                    const parsed = JSON.parse(cleaned);

                    window.__dsCompletions.push(parsed);

                  } catch {}
                }
              }
            }

            window.__lastCompletionRaw = full;

          }

          pump().catch(() => {});

        }

        if (url.includes('/upload')) {
          window.__dsUploads.push({
            url,
            status: response.status,
            ts: Date.now()
          });
        }

      } catch {}

      return response;
    };

  });
}

async function exportRuntime(page) {

  const runtime = await page.evaluate(() => ({
    fetches: window.__dsFetches || [],
    streams: window.__dsStreams || [],
    completions: window.__dsCompletions || [],
    uploads: window.__dsUploads || [],
    endpoints: window.__dsEndpoints || {},
    raw: window.__lastCompletionRaw || ''
  }));

  save(runtime);

  return runtime;
}

module.exports = {
  install,
  exportRuntime
};
JSEOF

echo "✅ Runtime stream intelligence installed."
echo ""
echo "Next:"
echo ""
echo "  1. require('./runtime-stream-intelligence')"
echo "  2. install(page)"
echo "  3. exportRuntime(page)"
echo ""
echo "Cache output:"
echo "  .cache/stream-intelligence.json"

