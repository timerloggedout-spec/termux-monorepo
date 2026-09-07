// Thin re-export wrapper: the actual MCP tool implementation lives in the
// `android-mcp` submodule (its own repo, its own history/CI). This file only
// exists so Vercel's zero-config API routing can mount it under /mcp/android
// from the mcp-hub's single deployment.
export { GET, POST, DELETE } from "../android-mcp/api/server";
