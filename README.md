# Jervis — a local assistant that runs tasks for you

Jervis is a small assistant you run on your own computer. You talk to it in a web
page (or the terminal, or by voice), and it **does things**: keeps a to-do list,
saves notes and reminders, tells you the time, lists your files, searches the web,
and opens apps or folders. Everything is stored in a SQLite file on your machine —
no account, no cloud, and no API key needed for the core features.

```
┌──────────────────────────────────────────────┐
│  Browser / terminal / microphone              │
│        ↓  "add task call the bank"            │
│  Jervis command router  →  SQLite memory      │
│        →  tasks · notes · reminders · system │
└──────────────────────────────────────────────┘
```

> **Where this came from:** the starting point is the open-source
> [Adib-07/Jervis](https://github.com/Adib-07/Jervis) project (MIT licence, see
> `LICENSE` and `UPSTREAM_README.md`). It was adapted here to work on Windows,
> macOS and Linux, to add a real to-do list with a clickable web panel, browser
> voice input/output, and a friendlier offline chat fallback. I couldn't find a
> link in your message, so this is the closest match to "Jervis that runs tasks
> for people and is interactive". Notes about the other projects I found are at
> the bottom of this file.

---

## Run it on your own computer

You need **Python 3.10 or newer**. That's it — the core uses only the Python
standard library, so there is nothing to install.

```bash
git clone https://github.com/warenkyle792-prog/jervis.git
cd jervis
python3 -m jarvis.web          # macOS / Linux
py -m jarvis.web               # Windows (or: python -m jarvis.web)
```

It prints `Jervis is running at http://127.0.0.1:8765` and normally opens your
browser automatically. If it doesn't, open <http://127.0.0.1:8765> yourself.
Press `Ctrl+C` in the terminal to stop it.

Shortcuts are included if you prefer double-clicking:

- **Windows:** `start.bat`
- **macOS / Linux:** `./start.sh`

Prefer a terminal instead of a web page?

```bash
python3 -m jarvis --text      # type commands, type `exit` to quit
python3 -m jarvis             # voice mode (falls back to typing without a mic)
```

Your data lives in `.jarvis_data/memory.sqlite3` (ignored by Git). Delete that
file to start fresh.

---

## What you can say

| Say this | What Jervis does |
|---|---|
| `add task call the bank` | Adds a task to your to-do list |
| `tasks` / `my tasks` | Shows the list with IDs |
| `complete 1` | Ticks task #1 off (say it again to reopen) |
| `delete task 1` | Removes task #1 |
| `clear completed` | Cleans up finished tasks |
| `remember the wifi code is 1234` | Saves a note |
| `notes` / `forget 1` | Lists / deletes notes |
| `remind me to call home at 18:30` | Saves a reminder |
| `reminders` / `done 1` | Lists / completes reminders |
| `time`, `date` | Current date and time |
| `status` | OS, machine, Python and disk info |
| `files` | Lists files in the folder Jervis was started in |
| `battery` | Battery level where the OS reports one |
| `apps`, `open app notepad`, `open folder ~/Downloads` | Apps and folders on your computer |
| `search web for weather in Nairobi` | Gives you a clickable search link |
| `help`, `capabilities`, `what can you do` | The full command list |
| `chat <anything>` | Free-form answer (needs an AI provider, see below) |

In the web UI you can also click checkboxes in **My Tasks**, use the **Quick
Actions** buttons, press the mic to speak (Chrome/Edge browser speech), and hear
replies read out loud. Typed commands work everywhere even without a microphone.

---

## Optional extras

**AI chat** (for open-ended questions instead of commands). Either:

```bash
# Option A: OpenAI
pip install -r requirements-optional.txt
set OPENAI_API_KEY=sk-...          # Windows:  set OPENAI_API_KEY=sk-...
python3 -m jarvis.web

# Option B: free, local Ollama
ollama pull llama3.2
ollama serve                      # leave running in another terminal
python3 -m jarvis.web
```

Without either, Jervis says it's offline and suggests a real command instead —
all task, note, reminder and system features still work.

**Terminal voice / offline speech:** `pip install -r requirements-optional.txt`
gives you `pyttsx3` and `SpeechRecognition`. On macOS, `brew install portaudio`
first, then `pip install pyaudio`. The web UI uses your browser's built-in speech
engine, so it needs none of this.

**Configuration** (environment variables, see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `JERVIS_HOST` | `127.0.0.1` | Interface to listen on (`0.0.0.0` for a LAN/preview) |
| `JERVIS_PORT` | `8765` | Web UI port |
| `JERVIS_NO_BROWSER` | unset | Set to `1` to stop auto-opening a browser |
| `JARVIS_DATA_DIR` | `.jarvis_data` | Where the SQLite database lives |
| `OPENAI_API_KEY` | unset | Enables OpenAI chat |
| `JARVIS_OLLAMA_URL` | `http://127.0.0.1:11434` | Local Ollama server |

---

## Tests

```bash
python3 -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python3 -m pytest -q
```

---

## If you meant a different "Jervis"

I looked these up while searching — tell me if one of them is the one you wanted
and I'll swap the setup over:

- **Desktop voice app that controls your PC/Mac** (mouse, keyboard, apps, music;
  Windows/macOS installers; the product was called *Jervis* before being renamed
  *Jarvis*): <https://arielzaha.github.io/jervis/> ·
  <https://github.com/TheJarvis-App/jarvis-app>
- **AI secretary web app** (chat, inbox, tasks, dashboards, voice):
  <https://github.com/dfaldu387/carlos-jervis>
- **Go task/automation runtime** (CLI, REST API, MCP):
  <https://github.com/saaedimam/jervis>
- **The original Jervis** (Jenkins CI job generator — not a personal assistant):
  <https://github.com/samrocketman/jervis>

---

## Licence

MIT. Upstream code © 2026 Adib Sunasra; adaptations in this repo keep the same
licence. See `LICENSE`.
