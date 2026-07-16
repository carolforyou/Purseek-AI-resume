@echo off
cd /d "%~dp0"
start "backend" /b "C:\Users\78708\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0backend\run_server.py"
start "frontend" /b "C:\Program Files\nodejs\node.exe" "%~dp0frontend\node_modules\vite\bin\vite.js" --host 0.0.0.0 --port 3000
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Servers started. Open browser and go to http://localhost:3000
pause
