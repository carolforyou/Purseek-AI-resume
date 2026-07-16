from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.custom_resume import router as custom_resume_router
from app.api.routes.health import router as health_router
from app.api.routes.jd import router as jd_router
from app.api.routes.interview import router as interview_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.profile import router as profile_router
from app.api.routes.resume import router as resume_router
from app.api.routes.resume_export import router as resume_export_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(profile_router, tags=["profile"])
api_router.include_router(resume_router, tags=["resume"])
api_router.include_router(resume_export_router, tags=["resume-export"])
api_router.include_router(jd_router, tags=["jd"])
api_router.include_router(custom_resume_router, tags=["custom-resume"])
api_router.include_router(knowledge_router, tags=["knowledge"])
api_router.include_router(interview_router, tags=["interview"])