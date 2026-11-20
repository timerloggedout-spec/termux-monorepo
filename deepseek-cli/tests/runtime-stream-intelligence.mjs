let runtime = {
  streams: [],
  fetches: [],
  events: [],
  sseChunks: []
};

export async function injectRuntimeHooks(page) {
  await page.evaluateOnNewDocument(() => {

    /* =========================
       GLOBAL RUNTIME BUFFERS
    ========================== */

    window.__STREAMS__ = [];
    window.__WS_MESSAGES__ = [];
    window.__FETCHES__ = [];
    window.__DOM_MUTATIONS__ = [];

    /* =========================
       FETCH STREAM INTELLIGENCE
    ========================== */

    const originalFetch = window.fetch;

    window.fetch = async (...args) => {
      const url = args?.[0]?.toString?.() || 'unknown';

      window.__FETCHES__.push({
        ts: Date.now(),
        url
      });

      const res = await originalFetch(...args);

      try {
        const cloned = res.clone();

        if (cloned.body) {
          const reader = cloned.body.getReader();
          const decoder = new TextDecoder();

          let full = '';

          async function pump() {
            while (true) {
              const { done, value } = await reader.read();

              if (done) break;

              const chunk = decoder.decode(value);

              full += chunk;

              window.__STREAMS__.push({
                ts: Date.now(),
                url,
                chunk
              });
            }

            window.__LAST_STREAM__ = {
              url,
              body: full
            };
          }

          pump();
        }
      } catch (e) {}

      return res;
    };

    /* =========================
       WEBSOCKET INTELLIGENCE
    ========================== */

    const OriginalWS = window.WebSocket;

    window.WebSocket = function (...args) {
      const ws = new OriginalWS(...args);

      window.__WS_MESSAGES__.push({
        ts: Date.now(),
        type: 'connect',
        url: args[0]
      });

      ws.addEventListener('message', ev => {
        window.__WS_MESSAGES__.push({
          ts: Date.now(),
          type: 'recv',
          data: ev.data
        });
      });

      const originalSend = ws.send;

      ws.send = function (data) {
        window.__WS_MESSAGES__.push({
          ts: Date.now(),
          type: 'send',
          data
        });

        return originalSend.call(this, data);
      };

      return ws;
    };

    /* =========================
       DOM MUTATION INTELLIGENCE
    ========================== */

    const obs = new MutationObserver(mutations => {
      for (const m of mutations) {
        window.__DOM_MUTATIONS__.push({
          ts: Date.now(),
          type: m.type,
          added: m.addedNodes.length,
          removed: m.removedNodes.length
        });
      }
    });

    obs.observe(document.documentElement, {
      subtree: true,
      childList: true,
      attributes: true
    });

  });
}


export async function exportRuntime(page) {
  runtime = runtime || {
    streams: [],
    fetches: [],
    events: [],
    sseChunks: []
  };

  return await page.evaluate(() => ({
    streams: window.__STREAMS__ || [],
    wsMessages: window.__WS_MESSAGES__ || [],
    fetches: window.__FETCHES__ || [],
    domMutations: window.__DOM_MUTATIONS__ || [],
    lastStream: window.__LAST_STREAM__ || null
  }));
}


export function getRuntime(){ return runtime; }
