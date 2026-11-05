@echo off
REM Start Jervis on Windows.
cd /d "%~dp0"
echo Starting Jervis at http://127.0.0.1:8765  (Ctrl+C to stop)
where py >nul 2>nul
if %errorlevel%==0 (
  py -m jarvis.web
) else (
  python -m jarvis.web
)
pause
