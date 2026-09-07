import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import * as androidHandlers from "../api/android";
import { withMcpAuth } from "../api/auth";
import * as termuxHandlers from "../api/termux";

const routes = [
  {
    path: "/mcp/termux",
    destination: "/api/termux",
    handlers: termuxHandlers,
  },
  {
    path: "/mcp/android",
    destination: "/api/android",
    handlers: androidHandlers,
  },
] as const;

test("Vercel wires each public MCP route to its API handler", async () => {
  const vercelConfig = JSON.parse(
    await readFile(new URL("../vercel.json", import.meta.url), "utf8"),
  ) as { rewrites: Array<{ source: string; destination: string }> };

  for (const route of routes) {
    assert.ok(
      vercelConfig.rewrites.some(
        (rewrite) =>
          rewrite.source === route.path && rewrite.destination === route.destination,
      ),
      `${route.path} must rewrite to ${route.destination}`,
    );
  }
});

test("each MCP route exports protected GET, POST, and DELETE handlers", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";

  try {
    for (const route of routes) {
      for (const method of ["GET", "POST", "DELETE"] as const) {
        assert.equal(typeof route.handlers[method], "function");

        const response = await route.handlers[method](
          new Request(`https://example.test${route.path}`, { method }),
        );
        assert.equal(response.status, 401, `${method} ${route.path} must require auth`);
        assert.equal(response.headers.get("www-authenticate"), "Bearer");
      }
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
    const response = await termuxHandlers.GET(
      new Request("https://example.test/mcp/termux"),
    );
    assert.equal(response.status, 503);
  } finally {
    if (previousToken !== undefined) {
      process.env.MCP_AUTH_TOKEN = previousToken;
    }
  }
});

test("authentication forwards requests with the configured Bearer token", async () => {
  const previousToken = process.env.MCP_AUTH_TOKEN;
  process.env.MCP_AUTH_TOKEN = "test-secret";
  let forwarded = false;
  const handler = withMcpAuth((request) => {
    forwarded = true;
    return new Response(request.method, { status: 202 });
  });

  try {
    const response = await handler(
      new Request("https://example.test/mcp/termux", {
        method: "POST",
        headers: { Authorization: "Bearer test-secret" },
      }),
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
