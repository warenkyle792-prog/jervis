from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import webbrowser

from jarvis.assistant import build_assistant
from jarvis.voice import Listener


ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = ROOT / "web"


def _speech_command(text: str) -> list[str]:
    """Best-effort server-side text-to-speech command for each platform."""
    system = platform.system()
    if system == "Darwin":
        return ["say", text]
    if system == "Windows":
        safe = text.replace("'", "''")
        return [
            "powershell",
            "-NoProfile",
            "-Command",
            "Add-Type -AssemblyName System.Speech; "
            f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')",
        ]
    exe = (
        shutil.which("espeak-ng")
        or shutil.which("espeak")
        or shutil.which("spd-say")
        or "espeak"
    )
    return [exe, text]


class JarvisWebHandler(SimpleHTTPRequestHandler):
    assistant = build_assistant()
    listener = Listener()

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    # --------------------------------------------------------------- helpers

    def _task_list(self) -> list[dict[str, object]]:
        try:
            items = self.assistant.context.memory.list_tasks()
            return [
                {
                    "id": task.id,
                    "body": task.body,
                    "done": task.done,
                    "created_at": task.created_at,
                }
                for task in items
            ]
        except Exception:
            return []

    # ------------------------------------------------------------------- GET

    def do_GET(self) -> None:
        if self.path == "/health":
            try:
                voice = bool(self.listener.available)
            except Exception:
                voice = False
            try:
                ai = bool(self.assistant.context.llm.available)
            except Exception:
                ai = False
            self._send_json(
                {
                    "ok": True,
                    "voice": voice,
                    "ai": ai,
                    "browser_voice": True,
                    "tasks": len(self._task_list()),
                }
            )
            return
        if self.path == "/api/tasks":
            self._send_json({"ok": True, "tasks": self._task_list()})
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    # ------------------------------------------------------------------ POST

    def do_POST(self) -> None:
        if self.path == "/api/command":
            self._handle_command()
            return
        if self.path == "/api/listen":
            self._handle_listen()
            return
        if self.path == "/api/speak":
            self._handle_speak()
            return
        if self.path == "/api/tasks":
            self._handle_tasks()
            return
        self.send_error(404)

    def _handle_command(self) -> None:
        body = self._read_json()
        if body is None:
            self._send_json({"ok": False, "response": "Invalid request."}, status=400)
            return

        command = str(body.get("command", "")).strip()
        response = self.assistant.handle(command)
        self._send_json({"ok": True, "command": command, "response": response})

    def _handle_tasks(self) -> None:
        body = self._read_json()
        if body is None:
            self._send_json({"ok": False, "error": "Invalid request."}, status=400)
            return

        memory = self.assistant.context.memory
        text = str(body.get("body", "")).strip()
        if text:
            memory.add_task(text)
            self._send_json({"ok": True, "tasks": self._task_list()})
            return

        raw_id = body.get("id")
        action = str(body.get("action", "toggle"))
        try:
            task_id = int(raw_id)
        except (TypeError, ValueError):
            self._send_json({"ok": False, "error": "Provide a task id."}, status=400)
            return

        if action == "delete":
            changed = memory.delete_task(task_id)
        else:
            changed = memory.toggle_task(task_id) is not None
        if not changed:
            self._send_json({"ok": False, "error": f"No task with id #{task_id}."}, status=404)
            return
        self._send_json({"ok": True, "tasks": self._task_list()})

    def _handle_listen(self) -> None:
        if not self.listener.available:
            self._send_json(
                {
                    "ok": False,
                    "error": self.listener.error or "Microphone input is unavailable.",
                },
                status=503,
            )
            return

        heard = self.listener.listen(timeout=6, phrase_time_limit=9)
        if heard.error:
            self._send_json({"ok": False, "error": heard.error}, status=422)
            return

        command = heard.text.strip()
        if not command:
            self._send_json({"ok": False, "error": "I did not hear a command."}, status=422)
            return

        response = self.assistant.handle(command)
        self._send_json({"ok": True, "command": command, "response": response})

    def _handle_speak(self) -> None:
        body = self._read_json()
        if body is None:
            self._send_json({"ok": False, "error": "Invalid request."}, status=400)
            return

        text = str(body.get("text", "")).strip()
        if not text:
            self._send_json({"ok": False, "error": "No speech text provided."}, status=400)
            return

        try:
            subprocess.Popen(_speech_command(text[:1200]))
        except OSError:
            # No server-side voice engine: let the browser speak instead.
            self._send_json(
                {"ok": False, "error": "Use browser speech synthesis."}, status=503
            )
            return
        self._send_json({"ok": True})

    def _read_json(self) -> dict[str, object] | None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        try:
            body = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        if not isinstance(body, dict):
            return None
        return body

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    host = os.environ.get("JERVIS_HOST", "127.0.0.1")
    port = int(os.environ.get("JERVIS_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), JarvisWebHandler)
    url = f"http://{'localhost' if host in ('0.0.0.0', '::') else host}:{server.server_port}"
    print(f"Jervis is running at {url} (listening on {host}:{server.server_port})", flush=True)

    if os.environ.get("JERVIS_NO_BROWSER") != "1" and host in ("127.0.0.1", "localhost"):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Jervis.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
