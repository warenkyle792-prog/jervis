# Third-party code and downloads

| What | Where it comes from | Licence | How it's used here |
|---|---|---|---|
| Jervis / Jarvis desktop voice assistant | [TheJarvis-App/jarvis-app](https://github.com/TheJarvis-App/jarvis-app) (v1.0.5) | MIT © 2026 Ariel and Shalev | Installers are linked and downloaded from the upstream GitHub Release. Source is fetched on demand by `get-source.sh` / `get-source.bat`, not vendored (≈54 MB of media assets). |
| Official product page | [arielzaha.github.io/jervis](https://arielzaha.github.io/jervis/) · [TheJarvis-App/jervis](https://github.com/TheJarvis-App/jervis) | — | Linked for reference; `site/index.html` is an original, self-contained page. |
| Browser Jervis assistant in `web-assistant/` | [Adib-07/Jervis](https://github.com/Adib-07/Jervis) | MIT © 2026 Adib Sunasra (see `web-assistant/LICENSE`) | Vendored and adapted: cross-platform system tasks, to-do list, browser voice, offline chat fallback. |
| Ollama + `llama3.2`, Whisper speech model | [ollama.com](https://ollama.com) | respective upstream licences | Downloaded by the desktop app itself on first run; nothing bundled here. |

Installer checksums are published by upstream in `SHA256SUMS.txt` on the release
page; `install-windows.ps1` and `install-mac.sh` verify against it.
