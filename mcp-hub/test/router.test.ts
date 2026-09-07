import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { GET, POST, DELETE } from "../api/mcp/[server].ts";
import { withMcpAuth } from "../api/auth.ts";

test("vercel.json rewrites every /mcp/:server path to the single dynamic router", async () => {
  const vercelConfig = JSON.parse(
    await readFile(new URL("../vercel.json", import.meta.url), "utf8")
  ) as { rewrites: Array<{ source: string; destination: string }> };

  assert.ok(
    vercelConfig.rewrites.some(
      (rewrite) =>
        rewrite.source === "/mcp/:server" && rewrite.destination === "/api/mcp/:server"
    ),
    "expected one generic /mcp/:server -> /api/mcp/:server rewrite, not one per host"
  );

  assert.ok(
    vercelConfig.rewrites.some(
      (rewrite) =>
        rewrite.source === "/mcp-hub/:server" && rewrite.destination === "/api/mcp/:server"
    ),
    "expected the /mcp-hub/:server alias to resolve to the same router"
  );
});

test("GET, POST, DELETE are exported as functions from the dynamic router", () => {
  assert.equal(typeof GET, "function", "GET must be exported as a function");
  assert.equal(typeof POST, "function", "POST must be exported as a function");
  assert.equal(typeof DELETE, "function", "DELETE must be exported as a function");
});

test("unauthenticated requests are rejected with 401 before server resolution", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";

  try {
    for (const server of ["termux", "android", "does-not-exist"]) {
      const response = await POST(
        new Request(`https://hub.test/api/mcp/${server}`, { method: "POST" })
      );
      assert.equal(response.status, 401, `${server} must require auth`);
      assert.equal(response.headers.get("www-authenticate"), "Bearer");
    }
  } finally {
    if (previousToken === undefined) {
      delete process.env.MCP_AUTH_TOKEN;
    } else {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});

test("authentication fails closed when MCP_AUTH_TOKEN is not configured", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  delete process.env.MCP_AUTH_TOKEN;

  try {
    const response = await GET(new Request("https://hub.test/api/mcp/termux"));
    assert.equal(response.status, 503);
  } finally {
    if (previousToken !== undefined) {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});

test("a known server resolves and forwards once authenticated", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";

  try {
    const response = await POST(
      new Request("https://hub.test/api/mcp/termux", {
        method: "POST",
        headers: {
          Authorization: "Bearer test-secret",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: 1,
          method: "initialize",
          params: {
            protocolVersion: "2024-11-05",
            capabilities: {},
            clientInfo: { name: "test", version: "0.0.0" },
          },
        }),
      })
    );
    assert.notEqual(response.status, 401, "a valid token must not be rejected");
    assert.notEqual(response.status, 404, "a known server must not 404");
  } finally {
    if (previousToken === undefined) {
      delete process.env.MCP_AUTH_TOKEN;
    } else {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});

test("an unknown server 404s with the known-hosts list once authenticated", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";

  try {
    const response = await POST(
      new Request("https://hub.test/api/mcp/does-not-exist", {
        method: "POST",
        headers: {
          Authorization: "Bearer test-secret",
          "content-type": "application/json",
        },
        body: JSON.stringify({}),
      })
    );
    assert.equal(response.status, 404);
    const body = await response.json();
    assert.ok(
      Array.isArray(body.known) && body.known.includes("termux") && body.known.includes("android"),
      "404 body must list the currently registered servers"
    );
  } finally {
    if (previousToken === undefined) {
      delete process.env.MCP_AUTH_TOKEN;
    } else {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});

test("withMcpAuth forwards the request once the configured token matches", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";
  let forwarded = false;
  const handler = withMcpAuth((request) => {
    forwarded = true;
    return new Response(request.method, { status: 202 });
  });

  try {
    const response = await handler(
      new Request("https://hub.test/api/mcp/termux", {
        method: "POST",
        headers: { Authorization: "Bearer test-secret" },
      })
    );

    assert.equal(response.status, 202);
    assert.equal(await response.text(), "POST");
    assert.equal(forwarded, true);
  } finally {
    if (previousToken === undefined) {
      delete process.env.MCP_AUTH_TOKEN;
    } else {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});