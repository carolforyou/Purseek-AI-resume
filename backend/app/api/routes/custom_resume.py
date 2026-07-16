from fastapi import APIRouter, HTTPException

from app.models.jd import CustomResumeRequest, CustomResumeResponse
from app.services.custom_resume_service import CustomResumeService

router = APIRouter()
custom_resume_service = CustomResumeService()


@router.post("/custom-resume", response_model=CustomResumeResponse)
def generate_custom_resume(request: CustomResumeRequest) -> CustomResumeResponse:
    result = custom_resume_service.generate_custom_resume(request.jd_id)
    if not result:
        raise HTTPException(status_code=404, detail="JD 不存在")
    return result