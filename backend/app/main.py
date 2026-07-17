from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.router import api_router

app = FastAPI(
    title="AI Job Hunt Assistant API",
    version="0.1.0",
)

# CORS — 同端口部署后允许所有来源，兼容开发与生产
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由 — 全部以 /api 开头
app.include_router(api_router)

# 前端静态文件 — 构建后自动挂载，覆盖根路径
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    print(f"[deploy] Frontend static files mounted from {frontend_dist}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000)
