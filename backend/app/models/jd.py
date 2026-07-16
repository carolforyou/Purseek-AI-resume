from pydantic import BaseModel


class JobDescription(BaseModel):
    id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    experience: str = ""
    education: str = ""
    job_type: str = ""
    industry: str = ""
    description: str = ""
    requirements: str = ""
    skills: list[str] = []
    responsibilities: list[str] = []


class MatchResult(BaseModel):
    jd_id: str
    jd_title: str
    jd_company: str
    total_score: float
    skill_score: float
    experience_score: float
    education_score: float
    preference_score: float
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


class CustomResumeRequest(BaseModel):
    jd_id: str
    resume_type: str = "custom"


class CustomResumeResponse(BaseModel):
    jd_id: str
    jd_title: str
    content: str
    modifications: list[str]