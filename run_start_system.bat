@echo off
REM Öffnet Git Bash und führt das start_system.sh Skript aus

setlocal
set PROJECT_PATH=C:\Users\Student\trading_system_workspace\trading_system_complete

REM Git Bash ausführen mit dem Skript
"C:\Program Files\Git\bin\bash.exe" -c "cd '%PROJECT_PATH%/scripts' && chmod +x start_system.sh && ./start_system.sh"
endlocal
pause
