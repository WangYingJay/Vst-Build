@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo === scan assets ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scan_assets.ps1"
if errorlevel 1 (
  echo scan_assets.ps1 failed
  exit /b 1
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
  echo ISCC.exe not found. Generated includes are ready; compile glbwl.iss manually.
  exit /b 0
)

echo === compile with "%ISCC%" ===
"%ISCC%" "%~dp0glbwl.iss"
exit /b %ERRORLEVEL%
