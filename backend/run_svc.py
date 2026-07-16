import sys, os
os.chdir(r'E:\学习\AI Job Hunt Assistant\backend')
sys.path.insert(0, r'E:\学习\AI Job Hunt Assistant\backend')
import uvicorn
uvicorn.run('app.main:app', host='0.0.0.0', port=8000)
