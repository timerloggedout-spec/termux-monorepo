import { withMcpAuth } from "../auth.js";
import {
  GET as termuxGET,
  POST as termuxPOST,
  DELETE as termuxDELETE,
} from "../../termux-mcp/api/server.js";
import {
  GET as androidGET,
  POST as androidPOST,
  DELETE as androidDELETE,
} from "../../android-mcp/api/server.js";

type Handler = (request: Request) => Response | Promise<Response>;

interface HostHandlers {
  GET: Handler;
  POST: Handler;
  DELETE: Handler;
}

// Adding a future MCP: add its submodule under mcp-hub/<name>, import its
// GET/POST/DELETE above, and add one entry here. No new file, no
// vercel.json edit — the rewrite in mcp-hub/vercel.json already forwards
// every /mcp/<name> path to this one router, and withMcpAuth below applies
// to every registered host uniformly.
const registry: Record<string, HostHandlers> = {
  termux: { GET: termuxGET, POST: termuxPOST, DELETE: termuxDELETE },
  android: { GET: androidGET, POST: androidPOST, DELETE: androidDELETE },
};

function resolveServer(request: Request): string | undefined {
  const segments = new URL(request.url).pathname.split("/").filter(Boolean);
  return segments[segments.length - 1];
}

function unknownServerResponse(server: string | undefined): Response {
  return new Response(
    JSON.stringify({
      error: "unknown MCP server",
      server: server ?? null,
      known: Object.keys(registry),
    }),
    { status: 404, headers: { "content-type": "application/json" } }
  );
}

// Every submodule handler is createMcpHandler(...) with no basePath override,
// so it only recognizes requests whose pathname is literally "/mcp" (that's
// where each was designed to be mounted standalone). Forwarded as-is, a
// request arriving here as "/mcp/termux" or "/mcp-hub/termux" fails that
// internal check and the submodule silently 404s its own generic response -
// not our unknownServerResponse, which never runs for a *known* server.
// Rewriting the path back to "/mcp" before delegating makes each submodule
// see exactly the URL shape it was built for, regardless of the outer prefix.
function asMcpRequest(request: Request): Request {
  const url = new URL(request.url);
  url.pathname = "/mcp";
  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers: request.headers,
    body: hasBody ? request.body : undefined,
  };
  // Node's fetch (undici) requires an explicit duplex mode whenever a
  // streaming body is attached to a Request/RequestInit.
  if (hasBody) init.duplex = "half";
  return new Request(url, init);
}

const dispatchGET: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.GET(asMcpRequest(request));
};

const dispatchPOST: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.POST(asMcpRequest(request));
};

const dispatchDELETE: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.DELETE(asMcpRequest(request));
};

// withMcpAuth wraps the whole dispatch, including the unknown-server case:
// an unauthenticated caller gets 401 before ever learning whether a given
// server name is registered, instead of a 404 leaking the known-hosts list.
export const GET = withMcpAuth(dispatchGET);
export const POST = withMcpAuth(dispatchPOST);
export const DELETE = withMcpAuth(dispatchDELETE);