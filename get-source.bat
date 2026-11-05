@echo off
REM Fetch the full upstream Jervis desktop app source (~54 MB).
cd /d "%~dp0"
if exist jervis-app-source\.git (
  echo Updating existing source...
  git -C jervis-app-source pull --ff-only
) else (
  git clone --depth 1 https://github.com/TheJarvis-App/jarvis-app.git jervis-app-source
)
echo.
echo Source is in .\jervis-app-source  (gitignored).
echo See jervis-app-source\README.md for run-from-source requirements.
pause
