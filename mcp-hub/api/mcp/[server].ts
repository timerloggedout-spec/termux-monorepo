import { withMcpAuth } from "../auth";
import {
  GET as termuxGET,
  POST as termuxPOST,
  DELETE as termuxDELETE,
} from "../../termux-mcp/api/server";
import {
  GET as androidGET,
  POST as androidPOST,
  DELETE as androidDELETE,
} from "../../android-mcp/api/server";

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

const dispatchGET: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.GET(request);
};

const dispatchPOST: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.POST(request);
};

const dispatchDELETE: Handler = async (request) => {
  const server = resolveServer(request);
  const entry = server ? registry[server] : undefined;
  if (!entry) return unknownServerResponse(server);
  return entry.DELETE(request);
};

// withMcpAuth wraps the whole dispatch, including the unknown-server case:
// an unauthenticated caller gets 401 before ever learning whether a given
// server name is registered, instead of a 404 leaking the known-hosts list.
export const GET = withMcpAuth(dispatchGET);
export const POST = withMcpAuth(dispatchPOST);
export const DELETE = withMcpAuth(dispatchDELETE);