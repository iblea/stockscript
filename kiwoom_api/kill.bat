@echo off

cd /d "%~dp0"

:: powershell
:: Set-ExecutionPolicy RemoteSigned



:: powershell -File background.ps1

powershell -ExecutionPolicy Bypass -File kill.ps1
