# Jervis — the desktop voice assistant

This is the **other Jervis**: the installable desktop app that actually does
things on your computer. Say **"Hey Jervis"**, then ask for music, videos, shows,
timers or documents — or have it use your mouse and keyboard for you. Its AI runs
**on your own computer**: no account, no API key, no cloud.

> The product was called **Jervis** through version 1.0.5 (the installer files
> still say Jervis); newer builds are branded *Jarvis*. Same app, same repo.

Upstream: <https://github.com/TheJarvis-App/jarvis-app> ·
Official page: <https://arielzaha.github.io/jervis/> ·
Latest release: **v1.0.5** (25 Sep 2026).

---

## 1. Download the installer

| Your computer | Download | Size |
|---|---|---|
| **Windows 10 / 11** | [Jervis.Setup.exe](https://github.com/TheJarvis-App/jarvis-app/releases/download/v1.0.5/Jervis.Setup.exe) | ~177 MB |
| **macOS (Apple silicon)** | [Jervis-Mac-arm64.dmg](https://github.com/TheJarvis-App/jarvis-app/releases/download/v1.0.5/Jervis-Mac-arm64.dmg) | ~196 MB |

Checksums: [SHA256SUMS.txt](https://github.com/TheJarvis-App/jarvis-app/releases/download/v1.0.5/SHA256SUMS.txt) ·
[All releases](https://github.com/TheJarvis-App/jarvis-app/releases)

Or use the one-command installers in this repo:

```powershell
# Windows — PowerShell (right-click → Run with PowerShell, or:)
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
```

```bash
# macOS
./install-mac.sh
```

Both scripts download the matching installer, verify it against the published
SHA256 sums, and then launch it for you.

---

## 2. Install

**Windows**
1. Run `Jervis.Setup.exe`.
2. If SmartScreen says *"Windows protected your PC"*, click **More info → Run anyway** (the signing certificate is still building reputation).
3. No admin rights needed. Jervis is added to the Start menu and desktop.

**macOS**
1. Open the `.dmg` and drag **Jervis** into **Applications**.
2. First launch: macOS may say it can't check for malware → **System Settings → Privacy & Security → Open Anyway**.
3. Grant the Accessibility permission when asked (that's what lets it click and type for you).

---

## 3. First start

On first launch Jervis downloads its local AI engine ([Ollama](https://ollama.com)),
the `llama3.2` model and an offline speech model — about **2.3 GB** on a Mac,
**3.6 GB** on Windows (only ~2.3 GB is kept; the NVIDIA libraries are unpacked
only on PCs with an NVIDIA GPU). Everything that doesn't need AI works while it
downloads. If you already run Ollama, it uses yours.

Then just say **"Hey Jervis"**. The app is ~190 MB to download and ~460 MB
installed. With 16 GB of RAM it can also see pictures and your screen (a 3 GB
vision model, downloaded only when you turn it on in **Settings → AI**).

Settings (gear, top right): microphone, voice, wake phrase, which AI answers,
computer control, weather city, privacy, optional services, start at login.
Your data lives in `%APPDATA%\Jarvis` (Windows) or
`~/Library/Application Support/Jarvis` (macOS).

**Requirements:** Windows 10/11 or macOS on Apple silicon. **Linux is not
supported** by the desktop app — see the fallback below.

---

## 4. The full source code is in this repo

The entire upstream app source is vendored in
[`jervis-app-source/`](jervis-app-source/) — **594 files, ~34 MB** (the upstream
clone is ~54 MB including its own `.git` history). It is a verbatim copy at commit
`7d06964` (2026-10-24); only the nested `.git/` directory was removed. See
[`jervis-app-source/VENDORED.md`](jervis-app-source/VENDORED.md) for provenance
and [`jervis-app-source/README.md`](jervis-app-source/README.md) for the
upstream documentation.

To run it from source you need Python 3.12 (3.11–3.14 on macOS), Node.js 20,
and on macOS `brew install portaudio`:

```bash
cd jervis-app-source
npm install
npm start              # Electron desktop window
```

Refresh the vendored copy from upstream with:

```bash
./get-source.sh        # macOS / Linux
get-source.bat         # Windows
```

Those scripts re-clone upstream and overwrite `jervis-app-source/` (keeping
`VENDORED.md`). Review `git status` afterwards before committing.

---

## 5. Linux / browser-only fallback

The desktop app has no Linux build, so the browser-based Jervis assistant from
the previous setup is still here in [`web-assistant/`](web-assistant/). It runs
tasks, notes, reminders and an interactive web UI with just Python 3.10+:

```bash
cd web-assistant
python3 -m jarvis.web       # then open http://127.0.0.1:8765
```

---

## Live preview in this workspace

`site/index.html` is a small download page with both installers and the setup
steps. Resume the preview on port 8000 with:

```bash
./start-preview.sh          # macOS / Linux
start-preview.bat           # Windows
```

Both bind `0.0.0.0:8000` (required for the Arena preview proxy) and serve `site/`.
It's a static page — no build step and no dependencies. To preview the
interactive browser assistant instead, run `python3 -m jarvis.web` from
`web-assistant/` (default port 8765; set `JERVIS_PORT=8000` to use the same port).

---

## Licence & attribution

The desktop app source is MIT © 2026 Ariel and Shalev
([`jervis-app-source/LICENSE`](jervis-app-source/LICENSE)). Installer binaries are
downloaded directly from their GitHub Releases — they are **not** redistributed
here. The browser fallback in `web-assistant/` is MIT © 2026 Adib Sunasra.
See [THIRD_PARTY.md](THIRD_PARTY.md).
