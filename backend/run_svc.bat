@echo off
set PYTHONUTF8=1
cd /d E:\??\AI Job Hunt Assistant\backend
"C:\Users\78708\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend_stdout.log 2> backend_stderr.log
