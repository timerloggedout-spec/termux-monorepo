import { withMcpAuth } from "./auth";
import {
  DELETE as androidDelete,
  GET as androidGet,
  POST as androidPost,
} from "../android-mcp/api/server";

// Thin wrapper: the actual MCP tool implementation lives in the
// `android-mcp` submodule (its own repo, its own history/CI). This file only
// exists so Vercel's zero-config API routing can mount it under /mcp/android
// from the mcp-hub's single deployment.
export const GET = withMcpAuth(androidGet);
export const POST = withMcpAuth(androidPost);
export const DELETE = withMcpAuth(androidDelete);
