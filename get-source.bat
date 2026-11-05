@echo off
REM Refresh the vendored Jervis desktop source in jervis-app-source\ from upstream.
REM Warning: overwrites everything in that folder except VENDORED.md.
setlocal
cd /d "%~dp0"
set "TMPDIR=%TEMP%\jervis-upstream-%RANDOM%"

echo Fetching upstream...
git clone --depth 1 -q https://github.com/TheJarvis-App/jarvis-app.git "%TMPDIR%"
if errorlevel 1 goto :fail
if exist "%TMPDIR%\.git" rmdir /s /q "%TMPDIR%\.git"

if not exist jervis-app-source mkdir jervis-app-source
for /d %%D in (jervis-app-source\*) do if /i not "%%~nxD"=="VENDORED.md" rmdir /s /q "%%D"
for %%F in (jervis-app-source\*) do if /i not "%%~nxF"=="VENDORED.md" del /q "%%F"

xcopy /E /I /Y /Q /H "%TMPDIR%\*" "jervis-app-source\" >nul
rmdir /s /q "%TMPDIR%"
echo Refreshed jervis-app-source\ from upstream.
echo Review changes with: git status
goto :eof

:fail
echo Clone failed. Nothing was changed.
if exist "%TMPDIR%" rmdir /s /q "%TMPDIR%"
exit /b 1
