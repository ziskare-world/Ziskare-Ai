"""
Ziskare AI - Autonomous REST API & Server Controller Microservice
================================================================
Independent daemon running on Python + PyTorch CUDA (GPU).
Provides:
  1. Offline LLM inference (/ask, /chat, /reset)
  2. Autonomous Server Control (/api/server/control: restart, start, stop, status)
  3. Server Filesystem Management (/api/server/fs: read, write, list)
  4. Real-time System & Server Diagnostics (/api/system, /api/server/logs)
  5. Standalone Web Rescue Console (GET /) for zero-downtime recovery
"""

import os
import sys
import json
import time
import psutil
import urllib.request
import subprocess
from pathlib import Path
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from ziskare_ai.core import ZiskareAI

WORKSPACE_DIR = Path(r"D:\Ziskare-space")
def get_node_server_url():
    port = 3002
    try:
        net_file = WORKSPACE_DIR / "data" / "network.json"
        if net_file.exists():
            data = json.loads(net_file.read_text(encoding="utf-8"))
            port = int(data.get("serverPort", 3002))
    except Exception:
        pass
    return f"http://127.0.0.1:{port}"

def is_node_server_running(url: str = get_node_server_url(), timeout: float = 1.0) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status in (200, 301, 302, 401, 403, 404)
    except Exception:
        return False

def get_system_telemetry():
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str(WORKSPACE_DIR.anchor))
    node_up = is_node_server_running()
    
    # Check PM2 processes if available
    pm2_status = "unavailable"
    try:
        out = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=3, shell=True)
        if out.returncode == 0 and out.stdout:
            pm2_status = json.loads(out.stdout)
    except Exception:
        pass

    return {
        "cpu_percent": cpu_percent,
        "memory": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        },
        "node_server_running": node_up,
        "workspace": str(WORKSPACE_DIR),
        "pm2": pm2_status
    }

def control_node_server(action: str):
    """Executes server lifecycle actions independently."""
    action = action.lower()
    if action == "status":
        return {
            "running": is_node_server_running(),
            "telemetry": get_system_telemetry()
        }

    if action == "restart":
        # First try PM2 restart
        try:
            res = subprocess.run(["pm2", "restart", "ziskare-space"], cwd=str(WORKSPACE_DIR), capture_output=True, text=True, timeout=10, shell=True)
            if res.returncode == 0:
                time.sleep(1.5)
                return {"success": True, "message": "Node.js server restarted via PM2", "output": res.stdout, "running": is_node_server_running()}
        except Exception:
            pass

        # Fallback: kill node processes running server.js or index.js and spawn anew
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmd = " ".join(proc.info.get('cmdline') or [])
                    if "node" in proc.info.get('name', '').lower() and ("index.js" in cmd or "server.js" in cmd):
                        proc.kill()
                except Exception:
                    pass
            time.sleep(1)
            # Start in background
            subprocess.Popen(["node", "index.js"], cwd=str(WORKSPACE_DIR), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0, shell=True)
            time.sleep(2)
            return {"success": True, "message": "Node.js server restarted via node index.js", "running": is_node_server_running()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "stop":
        try:
            res = subprocess.run(["pm2", "stop", "ziskare-space"], cwd=str(WORKSPACE_DIR), capture_output=True, text=True, timeout=8, shell=True)
            if res.returncode == 0:
                return {"success": True, "message": "Node.js server stopped via PM2", "running": is_node_server_running()}
        except Exception:
            pass

        try:
            killed = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmd = " ".join(proc.info.get('cmdline') or [])
                    if "node" in proc.info.get('name', '').lower() and ("index.js" in cmd or "server.js" in cmd):
                        proc.kill()
                        killed += 1
                except Exception:
                    pass
            return {"success": True, "message": f"Killed {killed} node server processes", "running": is_node_server_running()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    elif action == "start":
        if is_node_server_running():
            return {"success": True, "message": "Node.js server is already running!", "running": True}
        try:
            res = subprocess.run(["pm2", "start", "index.js", "--name", "ziskare-space"], cwd=str(WORKSPACE_DIR), capture_output=True, text=True, timeout=10, shell=True)
            if res.returncode == 0:
                time.sleep(1.5)
                return {"success": True, "message": "Node.js server started via PM2", "running": is_node_server_running()}
        except Exception:
            pass

        try:
            subprocess.Popen(["node", "index.js"], cwd=str(WORKSPACE_DIR), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0, shell=True)
            time.sleep(2)
            return {"success": True, "message": "Node.js server launched directly", "running": is_node_server_running()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return {"success": False, "error": f"Unknown action: {action}"}

def handle_filesystem_ops(action: str, rel_path: str, content: str = None):
    """Safely reads, writes, or lists files restricted to WORKSPACE_DIR."""
    try:
        target = (WORKSPACE_DIR / rel_path).resolve()
        # Security sandbox: must be within WORKSPACE_DIR
        if not str(target).startswith(str(WORKSPACE_DIR.resolve())):
            return {"success": False, "error": "Access denied: Path escapes workspace root."}

        if action == "read":
            if not target.exists():
                return {"success": False, "error": f"File not found: {rel_path}"}
            if target.is_dir():
                return {"success": False, "error": f"Path is a directory, not a file: {rel_path}"}
            data = target.read_text(encoding="utf-8", errors="replace")
            return {"success": True, "path": rel_path, "content": data, "bytes": len(data)}

        elif action == "write":
            if content is None:
                return {"success": False, "error": "Content is required for write action."}
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return {"success": True, "path": rel_path, "bytes_written": len(content)}

        elif action == "list":
            if not target.exists():
                return {"success": False, "error": f"Directory not found: {rel_path}"}
            items = []
            for entry in target.iterdir():
                items.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else None
                })
            return {"success": True, "path": rel_path, "items": items}

        return {"success": False, "error": f"Unknown filesystem action: {action}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_server_logs(max_lines: int = 50):
    logs = []
    logs_dir = WORKSPACE_DIR / "logs"
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            try:
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                logs.append({
                    "file": log_file.name,
                    "lines": lines[-max_lines:]
                })
            except Exception:
                pass
    return logs

RESCUE_CONSOLE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ziskare AI — Autonomous Rescue & Operations Console</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0b0f19;
  --card-bg: rgba(18, 24, 39, 0.85);
  --border: rgba(255, 255, 255, 0.08);
  --primary: #7c3aed;
  --primary-glow: rgba(124, 58, 237, 0.4);
  --accent: #06b6d4;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-image: radial-gradient(circle at 10% 20%, rgba(124, 58, 237, 0.15), transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.12), transparent 40%);
}
header {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  background: rgba(11, 15, 25, 0.7);
}
.brand { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 1.15rem; }
.badge {
  padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
}
.badge-node-online { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-node-offline { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); animation: pulse 1.5s infinite; }
.badge-ai { background: rgba(124, 58, 237, 0.2); color: #c084fc; border: 1px solid rgba(124, 58, 237, 0.35); }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.main-container {
  flex: 1; display: grid; grid-template-columns: 340px 1fr; gap: 20px; padding: 20px; max-width: 1400px; width: 100%; margin: 0 auto;
}
.panel {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
  backdrop-filter: blur(16px); padding: 20px; display: flex; flex-direction: column; gap: 16px;
}
.btn {
  background: #1e293b; color: var(--text); border: 1px solid var(--border);
  padding: 10px 16px; border-radius: 10px; font-weight: 600; font-size: 0.88rem;
  cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; justify-content: center;
}
.btn:hover { background: #334155; transform: translateY(-1px); }
.btn-primary { background: linear-gradient(135deg, #7c3aed, #6d28d9); border: none; box-shadow: 0 4px 15px var(--primary-glow); }
.btn-primary:hover { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.btn-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.btn-danger:hover { background: rgba(239, 68, 68, 0.35); }
.stat-box { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.stat-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; }
.chat-container { display: flex; flex-direction: column; height: 100%; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; max-height: calc(100vh - 280px); }
.msg { padding: 12px 16px; border-radius: 12px; max-width: 80%; line-height: 1.5; font-size: 0.92rem; }
.msg-user { align-self: flex-end; background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border-bottom-right-radius: 2px; }
.msg-ai { align-self: flex-start; background: #1e293b; border: 1px solid var(--border); border-bottom-left-radius: 2px; }
.chat-input-bar { display: flex; gap: 10px; padding-top: 12px; border-top: 1px solid var(--border); }
.chat-input { flex: 1; background: #0f172a; border: 1px solid var(--border); color: white; padding: 12px 16px; border-radius: 10px; font-size: 0.92rem; outline: none; }
.chat-input:focus { border-color: var(--primary); }
pre { background: #0f172a; padding: 8px 12px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; overflow-x: auto; margin-top: 6px; }
</style>
</head>
<body>
<header>
  <div class="brand">
    <span>🤖</span>
    <span>Ziskare AI Operations & Rescue Console</span>
    <span class="badge badge-ai">GPU Accelerated</span>
  </div>
  <div style="display: flex; gap: 10px; align-items: center;">
    <span id="nodeStatusBadge" class="badge badge-node-offline">Checking Node Server...</span>
    <a href="http://127.0.0.1:3002" target="_blank" class="btn" style="font-size: 0.8rem; padding: 6px 12px;">Open App ↗</a>
  </div>
</header>
<div class="main-container">
  <div class="panel">
    <h3 style="font-size: 1rem; color: var(--text-muted); text-transform: uppercase;">Server Control</h3>
    <button class="btn btn-primary" onclick="controlServer('restart')">⚡ Restart Node Server</button>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
      <button class="btn" onclick="controlServer('start')">▶ Start</button>
      <button class="btn btn-danger" onclick="controlServer('stop')">⏹ Stop</button>
    </div>
    <div class="stat-box">
      <div class="stat-row"><span>CPU Usage:</span><strong id="cpuVal">--%</strong></div>
      <div class="stat-row"><span>RAM Used:</span><strong id="ramVal">-- GB</strong></div>
      <div class="stat-row"><span>Disk Free:</span><strong id="diskVal">-- GB</strong></div>
      <div class="stat-row"><span>Node Server:</span><strong id="nodeVal">Detecting...</strong></div>
    </div>
    <h3 style="font-size: 1rem; color: var(--text-muted); text-transform: uppercase;">Quick Actions</h3>
    <button class="btn" onclick="askAi('Analyze why the server is not responding and check error logs')">📜 Check Error Logs</button>
    <button class="btn" onclick="askAi('Summarize current server hardware and load status')">📊 Telemetry Summary</button>
  </div>
  <div class="panel chat-container">
    <div class="chat-messages" id="chatBox">
      <div class="msg msg-ai">
        👋 <strong>Ziskare AI Rescue Daemon</strong> is active and independent. Even if the Node.js server stops, I can restart it, inspect logs, and modify files. How can I assist you?
      </div>
    </div>
    <div class="chat-input-bar">
      <input type="text" id="userInput" class="chat-input" placeholder="Ask Ziskare AI or give server commands (e.g., 'restart server')..." onkeydown="if(event.key==='Enter') sendUserMessage()">
      <button class="btn btn-primary" onclick="sendUserMessage()">Send</button>
    </div>
  </div>
</div>
<script>
async function refreshStatus() {
  try {
    const res = await fetch('/api/system');
    const data = await res.json();
    document.getElementById('cpuVal').textContent = data.cpu_percent + '%';
    document.getElementById('ramVal').textContent = data.memory.used_gb + ' / ' + data.memory.total_gb + ' GB';
    document.getElementById('diskVal').textContent = data.disk.free_gb + ' GB free';
    const badge = document.getElementById('nodeStatusBadge');
    const nodeVal = document.getElementById('nodeVal');
    if (data.node_server_running) {
      badge.textContent = 'Node Server: Online (3000)';
      badge.className = 'badge badge-node-online';
      nodeVal.textContent = 'Running [OK]';
      nodeVal.style.color = '#34d399';
    } else {
      badge.textContent = 'Node Server: Down / Offline';
      badge.className = 'badge badge-node-offline';
      nodeVal.textContent = 'STOPPED';
      nodeVal.style.color = '#f87171';
    }
  } catch(e) {}
}
setInterval(refreshStatus, 3000);
refreshStatus();

async function controlServer(action) {
  addMessage('Executing server ' + action + '...', 'ai');
  try {
    const res = await fetch('/api/server/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const result = await res.json();
    addMessage((result.success ? '✅ ' : '❌ ') + (result.message || result.error), 'ai');
    refreshStatus();
  } catch(err) {
    addMessage('❌ Error: ' + err.message, 'ai');
  }
}

function addMessage(text, role) {
  const box = document.getElementById('chatBox');
  const div = document.createElement('div');
  div.className = 'msg msg-' + role;
  div.innerHTML = text.replace(/\n/g, '<br>');
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

async function sendUserMessage() {
  const input = document.getElementById('userInput');
  const val = input.value.trim();
  if (!val) return;
  input.value = '';
  addMessage(val, 'user');
  
  // Intelligent command interception
  const lower = val.toLowerCase();
  if (lower.includes('restart') && lower.includes('server')) {
    controlServer('restart');
    return;
  }
  
  addMessage('Thinking...', 'ai');
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: val })
    });
    const data = await res.json();
    const lastMsg = document.getElementById('chatBox').lastElementChild;
    if (lastMsg && lastMsg.textContent === 'Thinking...') {
      lastMsg.innerHTML = (data.reply || 'No response').replace(/\n/g, '<br>');
    } else {
      addMessage(data.reply || 'No response', 'ai');
    }
  } catch(err) {
    addMessage('❌ Communication error: ' + err.message, 'ai');
  }
}

function askAi(prompt) {
  document.getElementById('userInput').value = prompt;
  sendUserMessage();
}
</script>
</body>
</html>'''

def create_handler(ai_instance: ZiskareAI):
    class ZiskareHandler(BaseHTTPRequestHandler):
        def _safe_write(self, data: bytes):
            try:
                self.wfile.write(data)
            except (ConnectionResetError, BrokenPipeError, Exception):
                pass
        def _set_headers(self, code=200, content_type='application/json'):
            try:
                self.send_response(code)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.end_headers()
            except (ConnectionResetError, BrokenPipeError):
                pass

        def do_OPTIONS(self):
            self._set_headers(200)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._set_headers(200, 'text/html; charset=utf-8')
                self._safe_write(RESCUE_CONSOLE_HTML.encode('utf-8'))

            elif self.path == "/health":
                self._set_headers(200)
                payload = {
                    "status": "healthy",
                    "service": "Ziskare AI",
                    "device": str(ai_instance.model.device),
                    "node_server_running": is_node_server_running()
                }
                self._safe_write(json.dumps(payload).encode())

            elif self.path == "/api/system":
                self._set_headers(200)
                data = get_system_telemetry()
                data["ai_device"] = str(ai_instance.model.device)
                self._safe_write(json.dumps(data).encode())

            else:
                self._set_headers(404)
                self._safe_write(b'{"error": "Endpoint Not Found"}')

        def do_POST(self):
            try:
                length = int(self.headers.get('content-length', 0))
                body = self.rfile.read(length).decode('utf-8', errors='replace') if length > 0 else ""
                try:
                    data = json.loads(body) if body else {}
                except Exception:
                    data = {}

                if self.path == "/ask":
                    prompt = data.get("prompt", "") or data.get("message", "")
                    max_tokens = int(data.get("max_new_tokens", 256))
                    temp = float(data.get("temperature", 0.3))
                    result = ai_instance.ask(
                        prompt,
                        max_new_tokens=max_tokens,
                        temperature=temp,
                        return_metrics=True
                    )
                    if isinstance(result, dict):
                        ans = result.get("answer", "") or result.get("reply", "")
                        result["reply"] = ans
                        result["answer"] = ans
                    self._set_headers(200)
                    self._safe_write(json.dumps(result).encode('utf-8'))

                elif self.path == "/chat":
                    msg = data.get("message", "") or data.get("prompt", "")
                    max_tokens = int(data.get("max_new_tokens", 256))
                    temp = float(data.get("temperature", 0.3))

                    # Check for autonomous server commands in the chat query
                    lower = msg.lower()
                    auto_action_report = ""
                    if "restart" in lower and "server" in lower:
                        res = control_node_server("restart")
                        auto_action_report = f"\n[Autonomous Action]: Server restart executed. Status: {res.get('message', 'done')}."

                    reply, stats = ai_instance.chat(
                        msg,
                        max_new_tokens=max_tokens,
                        temperature=temp
                    )
                    if auto_action_report:
                        reply += auto_action_report

                    self._set_headers(200)
                    payload = {"reply": reply, "answer": reply, "stats": stats}
                    self._safe_write(json.dumps(payload).encode('utf-8'))

                elif self.path == "/api/server/control":
                    action = data.get("action", "status")
                    result = control_node_server(action)
                    self._set_headers(200 if result.get("success", True) else 500)
                    self._safe_write(json.dumps(result).encode('utf-8'))

                elif self.path == "/api/server/fs":
                    action = data.get("action", "read")
                    path_str = data.get("path", "")
                    content = data.get("content", None)
                    result = handle_filesystem_ops(action, path_str, content)
                    self._set_headers(200 if result.get("success", True) else 400)
                    self._safe_write(json.dumps(result).encode('utf-8'))

                elif self.path == "/api/server/logs":
                    max_lines = int(data.get("lines", 50))
                    logs = get_server_logs(max_lines)
                    self._set_headers(200)
                    self._safe_write(json.dumps({"logs": logs}).encode('utf-8'))

                elif self.path == "/reset":
                    ai_instance.reset()
                    self._set_headers(200)
                    self._safe_write(b'{"status": "memory_reset"}')

                else:
                    self._set_headers(404)
                    self._safe_write(b'{"error": "Endpoint Not Found"}')

            except Exception as e:
                try:
                    self._set_headers(500)
                    self._safe_write(json.dumps({"success": False, "error": str(e), "reply": f"AI Daemon Error: {str(e)}"}).encode('utf-8'))
                except Exception:
                    pass

        def log_message(self, format, *args):
            pass

    return ZiskareHandler


def run_server(port: int = 5005, host: str = "127.0.0.1", ai_instance: ZiskareAI = None):
    """Launch the autonomous Ziskare AI REST API and Rescue Server."""
    if ai_instance is None:
        ai_instance = ZiskareAI()

    handler = create_handler(ai_instance)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"\n=======================================================", flush=True)
    print(f"  Ziskare AI - Autonomous Operations & Rescue Service", flush=True)
    print(f"  Console UI: http://{host}:{port}", flush=True)
    print(f"  API Endpoints: /ask, /chat, /api/system, /api/server/control", flush=True)
    print(f"  Press Ctrl+C to shutdown.", flush=True)
    print(f"=======================================================\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Ziskare AI] Server shutdown gracefully.", flush=True)
