@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\iniciar_pm2.ps1" %*
set "TCC_PM2_EXIT=%errorlevel%"
if not "%TCC_PM2_EXIT%"=="0" pause
exit /b %TCC_PM2_EXIT%
