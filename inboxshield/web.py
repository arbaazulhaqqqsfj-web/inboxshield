"""Dependency-free HTTP API and static web server."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .models import Ticket
from .orchestrator import InboxShield


ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
APP = InboxShield()


class Handler(SimpleHTTPRequestHandler):
    server_version = "InboxShield/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json({"status": "ok", "service": "inboxshield"})
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/triage":
            self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 20_000:
                raise ValueError("Request must be between 1 and 20,000 bytes.")
            payload = json.loads(self.rfile.read(content_length))
            subject = str(payload.get("subject", "")).strip()
            message = str(payload.get("message", "")).strip()
            if not subject or not message:
                raise ValueError("Subject and message are required.")
            if len(subject) > 200 or len(message) > 10_000:
                raise ValueError("Ticket exceeds the allowed length.")
            ticket = Ticket(
                subject=subject,
                message=message,
                customer_tier=str(payload.get("customer_tier", "standard")),
                channel=str(payload.get("channel", "email")),
            )
            self._json(APP.triage(ticket).to_dict())
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: object) -> None:
        # Avoid logging ticket contents or query strings.
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"InboxShield running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

