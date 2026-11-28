const headers = {
  "cache-control": "no-store",
  "content-type": "application/json; charset=utf-8",
};

/**
 * Public configuration-readiness endpoint for uptime monitors.
 *
 * This intentionally does not probe MCP submodules or expose tool metadata.
 * A 200 means the hub has its static bearer credential configured; it is not
 * proof that a downstream MCP handshake or tool call succeeds.
 */
export function GET(): Response {
  const authConfigured = Boolean(process.env.MCP_AUTH_TOKEN);

  return new Response(
    JSON.stringify({
      service: "mcp-hub",
      status: authConfigured ? "configured" : "not_ready",
      auth_mode: "static_bearer",
      auth_configured: authConfigured,
      mcp_protocol_probe: "not_performed",
      upstream_probe: "not_performed",
    }),
    {
      status: authConfigured ? 200 : 503,
      headers,
    }
  );
}
