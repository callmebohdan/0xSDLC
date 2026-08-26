@echo off
setlocal

python "%~dp0install.py" --force
exit /b %errorlevel%
