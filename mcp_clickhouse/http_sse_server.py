import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from .mcp_server import list_databases, list_tables, run_select_query


class SSEHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that streams responses using the SSE protocol."""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/list_databases":
            result = list_databases()
        elif path == "/list_tables":
            database = params.get("database", [None])[0]
            like = params.get("like", [None])[0]
            not_like = params.get("not_like", [None])[0]
            if not database:
                self.send_error(400, "database parameter required")
                return
            result = list_tables(database, like=like, not_like=not_like)
        elif path == "/run_select_query":
            query = params.get("query", [None])[0]
            if not query:
                self.send_error(400, "query parameter required")
                return
            result = run_select_query(query)
        else:
            self.send_error(404, "Not Found")
            return

        self.send_response(200)
        self.send_header("Content-type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        payload = json.dumps(result)
        self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))


def start_sse_server(port: int = 8000) -> None:
    """Start the HTTP SSE server on the given port."""
    server = HTTPServer(("0.0.0.0", port), SSEHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
