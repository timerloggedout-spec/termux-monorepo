import { withMcpAuth } from "./auth";
import {
  DELETE as termuxDelete,
  GET as termuxGet,
  POST as termuxPost,
} from "../termux-mcp/api/server";

// Thin wrapper: the actual MCP tool implementation lives in the
// `termux-mcp` submodule (its own repo, its own history/CI). This file only
// exists so Vercel's zero-config API routing can mount it under /mcp/termux
// from the mcp-hub's single deployment.
export const GET = withMcpAuth(termuxGet);
export const POST = withMcpAuth(termuxPost);
export const DELETE = withMcpAuth(termuxDelete);
