from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

app = FastAPI(
    title="AI Job Hunt Assistant API",
    version="0.1.0",
    description="AI 求职助手 MVP 后端服务",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "https://*.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Job Hunt Assistant API is running."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

# 部署时挂载前端静态文件
import os, pathlib
frontend_dist = pathlib.Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    print(f"[deploy] Frontend static files mounted from {frontend_dist}")
