from fastapi import APIRouter
from pydantic import BaseModel

from app.models.resume import ResumeDraftResponse, ResumeMarkdownResponse
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()


@router.get("/resume/draft", response_model=ResumeDraftResponse)
def get_resume_draft() -> ResumeDraftResponse:
    return resume_service.generate_draft()


class PolishRequest(BaseModel):
    section_id: str
    content: str


class PolishResponse(BaseModel):
    original: str
    polished: str
    changes: list[str]


class PolishFullResponse(BaseModel):
    content: str
    changes: list[str]


class ResumeLayoutSection(BaseModel):
    id: str
    title: str
    type: str = ""
    order: int
    visible: bool = True


class ResumeLayout(BaseModel):
    sections: list[ResumeLayoutSection]


@router.post("/resume/polish", response_model=PolishResponse)
def polish_resume_section(req: PolishRequest) -> PolishResponse:
    result = resume_service.polish_section(section_id=req.section_id, content=req.content)
    return PolishResponse(**result)


@router.post("/resume/polish-full", response_model=PolishFullResponse)
def polish_full_resume() -> PolishFullResponse:
    result = resume_service.polish_full()
    return PolishFullResponse(**result)


@router.get("/resume/layout", response_model=ResumeLayout)
def get_resume_layout() -> ResumeLayout:
    data = resume_service.get_layout()
    return ResumeLayout(**data)


@router.put("/resume/layout", response_model=ResumeLayout)
def update_resume_layout(layout: ResumeLayout) -> ResumeLayout:
    data = resume_service.update_layout(layout.model_dump())
    return ResumeLayout(**data)


@router.post("/resume/translate-to-english")
def translate_to_english() -> dict:
    result = resume_service.translate_to_english()
    return result
