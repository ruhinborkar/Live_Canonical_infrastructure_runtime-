@echo off
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "%~dp0"
if not exist node_modules (
  call npm.cmd install
)
call npm.cmd run dev
pause
