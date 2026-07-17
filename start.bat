@echo off
cd /d "%~dp0"

echo ========================================
echo  AI Job Hunt Assistant - 一键启动
echo ========================================
echo.

:: 1. 构建前端
echo [1/2] Building frontend...
cd frontend
call npx vite build 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] Frontend build failed, trying npm install first...
    call npm install
    call npx vite build
)
cd ..

:: 2. 启动后端（同时提供前端静态服务和 API）
echo [2/2] Starting server on http://localhost:3000
start "AI-Job-Hunt" /b "C:\Users\78708\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0backend\run_server.py"

echo.
echo ========================================
echo  Server is running at:
echo    http://localhost:3000
echo ========================================
echo  Press any key to stop...
pause >nul

:: 停止后端
taskkill /f /fi "WINDOWTITLE eq AI-Job-Hunt" >nul 2>&1
