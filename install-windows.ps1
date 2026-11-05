# Jervis desktop installer — Windows 10/11
# Run with:  powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
$ErrorActionPreference = "Stop"

$Version   = "v1.0.5"
$BaseUrl   = "https://github.com/TheJarvis-App/jarvis-app/releases/download/$Version"
$ExeName   = "Jervis.Setup.exe"
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Installer = Join-Path $Downloads $ExeName
$SumsFile  = Join-Path $Downloads "Jervis-SHA256SUMS.txt"

New-Item -ItemType Directory -Force -Path $Downloads | Out-Null

Write-Host "Downloading Jervis $Version (~177 MB)..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$BaseUrl/$ExeName" -OutFile $Installer
Write-Host "Saved to $Installer"

Write-Host "Checking the published SHA256 checksum..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$BaseUrl/SHA256SUMS.txt" -OutFile $SumsFile
    $line = Get-Content $SumsFile | Where-Object { $_ -match [regex]::Escape($ExeName) } | Select-Object -First 1
    if ($line) {
        $expected = ($line -split '\s+')[0].ToUpperInvariant()
        $actual   = (Get-FileHash -Algorithm SHA256 -Path $Installer).Hash.ToUpperInvariant()
        if ($expected -ne $actual) {
            throw "Checksum mismatch. Expected $expected but got $actual. The file was NOT launched."
        }
        Write-Host "Checksum OK." -ForegroundColor Green
    } else {
        Write-Host "Checksum file did not list $ExeName; skipping verification." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not verify checksum: $_" -ForegroundColor Yellow
    Write-Host "Continuing anyway — download manually from https://github.com/TheJarvis-App/jarvis-app/releases/latest if unsure."
}

Write-Host "Launching the installer..." -ForegroundColor Cyan
Start-Process -FilePath $Installer
Write-Host ""
Write-Host "If SmartScreen says 'Windows protected your PC', click More info -> Run anyway." -ForegroundColor Yellow
Write-Host "When it's done, find Jervis in your Start menu and say 'Hey Jervis'." -ForegroundColor Green
