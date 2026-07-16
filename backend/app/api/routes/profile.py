from fastapi import APIRouter

from app.models.profile import ExtractValueRequest, ExtractValueResponse, ProfileData, ProfileUpdateRequest
from app.services.profile_service import ProfileService

router = APIRouter()
profile_service = ProfileService()


@router.put("/profile/save", response_model=ProfileData)
def save_profile(profile: ProfileData) -> ProfileData:
    profile_service.save_profile(profile)
    return profile


@router.get("/profile/export")
def export_profile() -> dict:
    p = profile_service.get_profile()
    return {"filename": "profile.json", "content": p.model_dump()}


@router.get("/profile", response_model=ProfileData)
def get_profile() -> ProfileData:
    return profile_service.get_profile()


@router.post("/profile/extract", response_model=ExtractValueResponse)
def extract_value(request: ExtractValueRequest) -> ExtractValueResponse:
    section_map = {
        "basic_info": "基本信息",
        "self_intro": "自我介绍",
        "work_experience": "工作经验",
        "skills": "个人技能",
        "education": "教育背景",
        "project_experience": "项目经验",
        "awards": "获奖情况",
        "self_evaluation": "自我评价",
    }
    extracted_section = section_map.get(request.stage, "经历片段")

    profile = profile_service.extract_from_conversation(
        stage=request.stage,
        user_message=request.user_message,
        assistant_summary=request.assistant_summary,
    )

    return ExtractValueResponse(
        message="已通过 AI 提取并保存简历信息",
        extracted_section=extracted_section,
        profile=profile,
    )


@router.patch("/profile", response_model=ProfileData)
def update_profile(request: ProfileUpdateRequest) -> ProfileData:
    return profile_service.update_field(field_path=request.field_path, value=request.value)
