from pydantic import BaseModel


class ResumeProjectDraft(BaseModel):
    title: str = ""
    bullets: list[str] = []


class ResumeEducationDraft(BaseModel):
    title: str = ""
    bullets: list[str] = []


class ResumeDraftResponse(BaseModel):
    summary: str = ""
    skills: list[str] = []
    projects: list[ResumeProjectDraft] = []
    education: list[ResumeEducationDraft] = []


class ResumeMarkdownResponse(BaseModel):
    content: str = ""
