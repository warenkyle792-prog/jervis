from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import urllib.parse
import webbrowser


@dataclass(frozen=True)
class Capability:
    command: str
    description: str
    examples: tuple[str, ...]


CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        "capabilities",
        "List the system tasks Jervis knows how to perform.",
        ("capabilities", "what can you do"),
    ),
    Capability(
        "apps",
        "List installed applications found in common application folders.",
        ("apps", "list apps"),
    ),
    Capability(
        "open app <name>",
        "Launch an application on macOS, Windows or Linux.",
        ("open app Calculator", "launch notepad"),
    ),
    Capability(
        "open folder <path>",
        "Open a folder in your file manager.",
        ("open folder .", "open folder ~/Downloads"),
    ),
    Capability(
        "search web for <query>",
        "Give you a ready-to-click web search link.",
        ("search web for weather in Nairobi", "google Python speech recognition"),
    ),
    Capability(
        "time",
        "Show the current date and time.",
        ("time", "what time is it"),
    ),
    Capability(
        "battery",
        "Show battery status when the machine reports one.",
        ("battery", "battery status"),
    ),
    Capability(
        "files",
        "List files in the current workspace directory.",
        ("files", "list files"),
    ),
)


def capabilities() -> str:
    lines = ["System tasks I can perform:"]
    for capability in CAPABILITIES:
        example = capability.examples[0]
        lines.append(f"  {capability.command}: {capability.description} Example: `{example}`")
    lines.append("  To-do list: `add task <thing>`, `tasks`, `complete <id>` (see `help`)")
    return "\n".join(lines)


def list_apps(limit: int = 80) -> str:
    system = platform.system()
    app_dirs: list[Path] = []
    if system == "Darwin":
        app_dirs = [Path("/Applications"), Path.home() / "Applications"]
    elif system == "Windows":
        app_dirs = [
            Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
            / "Microsoft/Windows/Start Menu/Programs",
            Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs",
        ]
    else:
        app_dirs = [Path("/usr/share/applications"), Path.home() / ".local/share/applications"]

    apps: list[str] = []
    for app_dir in app_dirs:
        if not app_dir.exists():
            continue
        pattern = "*.app" if system == "Darwin" else ("*.lnk" if system == "Windows" else "*.desktop")
        for app in app_dir.glob(pattern):
            apps.append(app.stem)

    if not apps:
        return (
            "I could not find an applications folder on this computer. "
            "You can still use `open app <command>` to launch something by name."
        )

    names = sorted(set(apps), key=str.lower)
    visible = names[:limit]
    suffix = "" if len(names) <= limit else f"\n...and {len(names) - limit} more."
    return "Installed apps:\n" + "\n".join(f"  {name}" for name in visible) + suffix


def open_app(name: str) -> str:
    app_name = name.strip()
    if not app_name:
        return "Use `open app <name>`."

    system = platform.system()
    if system == "Darwin":
        result = subprocess.run(
            ["open", "-a", app_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return f"Opened {app_name}."
        detail = result.stderr.strip() or result.stdout.strip()
        return f"I could not open {app_name}. {detail}".strip()

    if system == "Windows":
        try:
            os.startfile(app_name)  # type: ignore[attr-defined]
            return f"Opened {app_name}."
        except (OSError, AttributeError) as exc:
            return f"I could not open {app_name}. {exc}"

    executable = shutil.which(app_name)
    if not executable:
        return (
            f"I could not find an app called {app_name!r} on this computer. "
            f"Try `search web for {app_name}` instead."
        )
    try:
        subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Launched {app_name}."
    except OSError as exc:
        return f"I could not launch {app_name}. {exc}"


def open_folder(raw_path: str) -> str:
    path_text = raw_path.strip() or "."
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        return f"Folder does not exist: {path}"
    if not path.is_dir():
        return f"That path is not a folder: {path}"

    system = platform.system()
    if system == "Darwin":
        command = ["open", str(path)]
    elif system == "Windows":
        command = ["explorer", str(path)]
    else:
        command = ["xdg-open", str(path)]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=5)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"Here's the folder path: {path} (no file manager available here: {exc})"

    if result.returncode == 0:
        return f"Opened folder {path}."
    detail = result.stderr.strip() or result.stdout.strip()
    return f"I could not open {path}. {detail}".strip()


def search_web(query: str) -> str:
    cleaned = query.strip()
    if not cleaned:
        return "Use `search web for <query>`."
    encoded = urllib.parse.urlencode({"q": cleaned})
    url = f"https://www.google.com/search?{encoded}"
    if os.environ.get("JERVIS_NO_BROWSER") != "1":
        try:
            webbrowser.open(url)
        except Exception:  # Headless servers have no browser; the link still works.
            pass
    return f"Searching the web for: {cleaned}\n{url}"


def current_time() -> str:
    return datetime.now().strftime("It is %A, %Y-%m-%d %H:%M:%S.")


def battery_status() -> str:
    system = platform.system()
    if system == "Darwin":
        result = subprocess.run(
            ["pmset", "-g", "batt"], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            return f"I could not read battery status. {detail}".strip()
        output = " ".join(line.strip() for line in result.stdout.splitlines())
        percent = re.search(r"(\d+%)", output)
        charging = "charging" if "AC Power" in output else "not charging"
        if percent:
            return f"Battery is {percent.group(1)} and {charging}."
        return output or "Battery status is unavailable."

    if system == "Linux":
        supply = Path("/sys/class/power_supply")
        try:
            for battery in supply.glob("BAT*"):
                capacity = (battery / "capacity").read_text().strip()
                state = (battery / "status").read_text().strip().lower()
                return f"Battery is {capacity}% and {state}."
        except OSError:
            pass
        return "Battery status is unavailable — this machine reports no battery (desktop or virtual machine)."

    return "Battery status is not available on this platform yet."


def list_workspace_files(limit: int = 80) -> str:
    root = Path.cwd()
    entries = sorted(root.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    if not entries:
        return f"No files found in {root}."
    visible = entries[:limit]
    lines = [f"Files in {root}:"]
    for entry in visible:
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"  {entry.name}{suffix}")
    if len(entries) > limit:
        lines.append(f"...and {len(entries) - limit} more.")
    return "\n".join(lines)
