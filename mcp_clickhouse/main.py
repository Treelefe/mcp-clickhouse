import argparse

from .mcp_server import mcp
from .http_sse_server import start_sse_server


def main():
    parser = argparse.ArgumentParser(description="Run the ClickHouse MCP server")
    parser.add_argument(
        "--http-port",
        type=int,
        help="If set, run an additional HTTP SSE server on this port",
    )
    args = parser.parse_args()

    if args.http_port:
        import threading

        server_thread = threading.Thread(
            target=start_sse_server, args=(args.http_port,), daemon=True
        )
        server_thread.start()

    mcp.run()


if __name__ == "__main__":
    main()
