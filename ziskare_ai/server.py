"""
Ziskare AI - Lightweight REST API Microservice
==============================================
Zero-dependency HTTP server exposing Ziskare AI to any programming language.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from ziskare_ai.core import ZiskareAI


def create_handler(ai_instance: ZiskareAI):
    class ZiskareHandler(BaseHTTPRequestHandler):
        def _set_headers(self, code=200):
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

        def do_OPTIONS(self):
            self._set_headers(200)

        def do_GET(self):
            if self.path == "/health":
                self._set_headers(200)
                payload = {
                    "status": "healthy",
                    "service": "Ziskare AI",
                    "device": str(ai_instance.model.device)
                }
                self.wfile.write(json.dumps(payload).encode())
            else:
                self._set_headers(404)
                self.wfile.write(b'{"error": "Endpoint Not Found"}')

        def do_POST(self):
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body) if body else {}

            if self.path == "/ask":
                prompt = data.get("prompt", "")
                max_tokens = int(data.get("max_new_tokens", 256))
                temp = float(data.get("temperature", 0.3))
                result = ai_instance.ask(
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=temp,
                    return_metrics=True
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode())

            elif self.path == "/chat":
                msg = data.get("message", "")
                max_tokens = int(data.get("max_new_tokens", 256))
                temp = float(data.get("temperature", 0.3))
                reply, stats = ai_instance.chat(
                    msg,
                    max_new_tokens=max_tokens,
                    temperature=temp
                )
                self._set_headers(200)
                self.wfile.write(json.dumps({"reply": reply, "stats": stats}).encode())

            elif self.path == "/reset":
                ai_instance.reset()
                self._set_headers(200)
                self.wfile.write(b'{"status": "memory_reset"}')
            else:
                self._set_headers(404)
                self.wfile.write(b'{"error": "Endpoint Not Found"}')

        def log_message(self, format, *args):
            # Suppress default noisy access logs
            pass

    return ZiskareHandler


def run_server(port: int = 5005, host: str = "127.0.0.1", ai_instance: ZiskareAI = None):
    """
    Launch the Ziskare AI REST API server.
    """
    if ai_instance is None:
        ai_instance = ZiskareAI()

    handler = create_handler(ai_instance)
    server = HTTPServer((host, port), handler)
    print(f"\n=======================================================", flush=True)
    print(f"  Ziskare AI - Universal REST API Service", flush=True)
    print(f"  Host: http://{host}:{port}", flush=True)
    print(f"  Endpoints: POST /ask, POST /chat, GET /health", flush=True)
    print(f"  Press Ctrl+C to shutdown.", flush=True)
    print(f"=======================================================\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Ziskare AI] Server shutdown gracefully.", flush=True)
