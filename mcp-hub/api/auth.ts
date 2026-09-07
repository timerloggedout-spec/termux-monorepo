import { createHash, timingSafeEqual } from "node:crypto";

type McpHandler = (request: Request) => Response | Promise<Response>;

function tokensMatch(providedToken: string, configuredToken: string): boolean {
  const provided = createHash("sha256").update(providedToken).digest();
  const configured = createHash("sha256").update(configuredToken).digest();

  return timingSafeEqual(provided, configured);
}

export function withMcpAuth(handler: McpHandler): McpHandler {
  return (request) => {
    const configuredToken = process.env.MCP_AUTH_TOKEN;
    if (!configuredToken) {
      return new Response("MCP authentication is not configured", { status: 503 });
    }

    const authorization = request.headers.get("authorization");
    const providedToken = authorization?.startsWith("Bearer ")
      ? authorization.slice("Bearer ".length)
      : undefined;

    if (!providedToken || !tokensMatch(providedToken, configuredToken)) {
      return new Response("Unauthorized", {
        status: 401,
        headers: { "WWW-Authenticate": "Bearer" },
      });
    }

    return handler(request);
  };
}
