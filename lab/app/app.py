"""Small, dependency-free teaching application. Do not use as a production server."""
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        code = 200
        if path == "/healthz":
            body = {"status": "alive"}
        elif path == "/readyz":
            ready = not Path("/tmp/not-ready").exists()
            code = 200 if ready else 503
            body = {"status": "ready" if ready else "not ready"}
        elif path == "/":
            body = {
                "application": "AHEAD PPFCU HTTP Lab",
                "message": os.environ.get("APP_MESSAGE", "Hello from Podman"),
                "version": os.environ.get("APP_VERSION", "v1"),
                "pod": socket.gethostname(),
                "uid": os.getuid(),
            }
        else:
            code, body = 404, {"error": "not found"}
        payload = (json.dumps(body) + "\n").encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(json.dumps({"remote": self.client_address[0], "request": fmt % args}), flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(json.dumps({"event": "starting", "port": port, "uid": os.getuid()}), flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
