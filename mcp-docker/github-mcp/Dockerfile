# Optional thin wrapper. Prefer the official public image directly:
#   ghcr.io/github/github-mcp-server:latest
#
# This Dockerfile exists only if you need to pin, add labels, or inject
# a custom entrypoint. Upstream is Go + distroless; do not reinstall the
# old npm package @modelcontextprotocol/server-github (archived / unsupported).

FROM ghcr.io/github/github-mcp-server:latest

LABEL org.opencontainers.image.title="github-mcp-server (org wrapper)"
LABEL org.opencontainers.image.description="Self-host lane for timerloggedout-spec — separated from Vercel mcp-hub"
LABEL org.opencontainers.image.source="https://github.com/timerloggedout-spec/termux-monorepo"

# Default remains the upstream ENTRYPOINT. Override at runtime:
#   docker run … http          # Streamable HTTP on 8082
#   docker run -i …            # stdio (default)
