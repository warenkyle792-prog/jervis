@echo off
REM Resume the Jervis preview on port 8000 (bind 0.0.0.0 for the preview proxy).
cd /d "%~dp0"
if not exist site\index.html (
  echo site\index.html is missing — cannot start the preview.
  exit /b 1
)
echo Jervis preview: http://localhost:8000
python -m http.server 8000 --bind 0.0.0.0 --directory site
pause
