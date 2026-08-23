import os
import sys


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_TRANSPORT = "stdio"
ALLOWED_TRANSPORTS = {"stdio", "sse", "streamable-http"}
NETWORK_TRANSPORTS = {"sse", "streamable-http"}

try:
    from termux_mcp_server import mcp
except ImportError:
    termux_mcp_dir = os.environ.get("TERMUX_MCP_DIR")
    if termux_mcp_dir:
        sys.path.insert(0, termux_mcp_dir)
        try:
            from termux_mcp_server import mcp
        except ImportError as exc:
            print(f"Import of termux_mcp_server failed: {exc}", file=sys.stderr)
            mcp = None
    else:
        mcp = None

if mcp is None:
    print(
        "Could not import termux_mcp_server. Install the fork with "
        "'pip install -e /path/to/termux-mcp-server-fork' or set "
        "TERMUX_MCP_DIR to its checkout.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def main():
    transport = os.environ.get("TERMUX_MCP_TRANSPORT", DEFAULT_TRANSPORT)
    host = os.environ.get("TERMUX_MCP_HOST", DEFAULT_HOST)
    port = int(os.environ.get("TERMUX_MCP_PORT", str(DEFAULT_PORT)))
    if transport not in ALLOWED_TRANSPORTS:
        allowed = ", ".join(sorted(ALLOWED_TRANSPORTS))
        print(
            f"Invalid TERMUX_MCP_TRANSPORT {transport!r}; choose one of: {allowed}.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if transport in NETWORK_TRANSPORTS:
        mcp.settings.host = host
        mcp.settings.port = port

    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
