@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

where pwsh >nul 2>nul
if not errorlevel 1 goto run_powershell

where bash >nul 2>nul
if not errorlevel 1 goto run_bash

echo Error: neither pwsh nor bash is available in PATH.
echo Install PowerShell 7+ or Bash, then run this script again.
exit /b 1

:run_powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%bootstrap-auditor.ps1" %*
exit /b %ERRORLEVEL%

:run_bash
bash "%SCRIPT_DIR%bootstrap-auditor.sh" %*
exit /b %ERRORLEVEL%
