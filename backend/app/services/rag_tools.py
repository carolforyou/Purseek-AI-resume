"LangChain tools for the AI Job Hunt Agent.

Each tool is a self-contained function that the agent can call
to accomplish specific tasks.
"""

from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.services.jd_service import JDService
from app.services.knowledge_base import get_knowledge_base
from app.services.profile_service import ProfileService
from app.services.resume_service import ResumeService


class SearchKBInput(BaseModel):
    query: str = Field(description="Search query for the knowledge base")


class AnalyzeJDInput(BaseModel):
    jd_text: str = Field(description="Full text of the job description to analyze")


class CustomResumeInput(BaseModel):
    jd_id: str = Field(description="ID of the job description to customize for")


class PolishInput(BaseModel):
    content: str = Field(description="Content to polish")
    style: str = Field(default="professional", description="Style: professional, concise, technical")


@tool(args_schema=SearchKBInput)
def search_knowledge_base(query: str) -> str:
    """Search the personal knowledge base for relevant information.
    
    Use this when the user asks about their own resume content, 
    work experience, skills, or any information stored in the knowledge base.
    """
    kb = get_knowledge_base()
    results = kb.search(query, k=5)
    if not results:
        return "Knowledge base is empty. Upload some documents first."

    lines = ["Found relevant information from your knowledge base:"]
    for i, (text, score) in enumerate(results, 1):
        lines.append(f"\n--- Result {i} (score: {score:.2f}) ---")
        lines.append(text[:300])
    return "\n".join(lines)


@tool(args_schema=AnalyzeJDInput)
def analyze_jd(jd_text: str) -> str:
    """Analyze a job description and extract structured requirements.
    
    Use this when the user pastes a job description and wants to understand
    the key requirements, skills needed, and how to prepare.
    """
    jd_service = JDService()
    result = jd_service.parse_jd_text(jd_text)

    lines = [
        f"Job Title: {result.get('title', 'Unknown')}",
        f"Company: {result.get('company', 'Unknown')}",
        f"Location: {result.get('location', 'Unknown')}",
        f"\nRequired Skills: {', '.join(result.get('skills', []))}",
        f"\nDescription: {result.get('description', '')[:300]}",
        f"\nRequirements: {result.get('requirements', '')[:300]}",
    ]
    return "\n".join(lines)


@tool(args_schema=CustomResumeInput)
def generate_custom_resume(jd_id: str) -> str:
    """Generate a resume customized for a specific job description.
    
    Use this when the user wants to create a tailored resume for a specific job.
    """
    from app.services.custom_resume_service import CustomResumeService
    service = CustomResumeService()
    result = service.generate_custom_resume(jd_id)
    if not result:
        return "Could not generate custom resume. Make sure you have saved the job description first."

    lines = [
        f"Custom resume generated for: {result.jd_title}",
        f"\n{result.content[:2000]}",
        f"\n\nModifications made:",
    ]
    for mod in result.modifications:
        lines.append(f"  - {mod}")
    return "\n".join(lines)


@tool(args_schema=PolishInput)
def polish_content(content: str, style: str = "professional") -> str:
    """Polish and improve resume content.
    
    Use this to improve the wording of any section in the resume.
    """
    resume_service = ResumeService()
    result = resume_service.polish_section("general", content)
    return result.get("polished", content)


@tool
def get_profile_summary() -> str:
    """Get a summary of the current user profile/resume.
    
    Use this when you need to know the user's background, skills, or experience.
    """
    profile_service = ProfileService()
    profile = profile_service.get_profile()

    lines = [
        f"Name: {profile.basic_info.name or 'Not set'}",
        f"Job Intention: {profile.basic_info.job_intention or 'Not set'}",
        f"Email: {profile.basic_info.email or 'Not set'}",
        f"Phone: {profile.basic_info.phone or 'Not set'}",
        f"Degree: {profile.basic_info.highest_degree or 'Not set'}",
        f"\nSkills: {', '.join(profile.skills[:10]) if profile.skills else 'None'}",
        f"\nWork Experiences: {len(profile.work_experiences)}",
        f"Projects: {len(profile.project_experiences)}",
        f"Education entries: {len(profile.education)}",
    ]
    for exp in profile.work_experiences[:2]:
        lines.append(f"  - {exp.company_name} / {exp.position_name} ({exp.work_time})")
    return "\n".join(lines)


ALL_TOOLS = [
    search_knowledge_base,
    analyze_jd,
    generate_custom_resume,
    polish_content,
    get_profile_summary,
]
