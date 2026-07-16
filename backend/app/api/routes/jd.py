from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.jd import JobDescription, MatchResult
from app.services.jd_service import JDService
from app.services.liepin_mcp_service import LiepinJobItem, LiepinMCPService

router = APIRouter()
jd_service = JDService()
liepin_service = LiepinMCPService()


# ===== 本地 JD CRUD =====

@router.get("/jd", response_model=list[JobDescription])
def get_all_jds() -> list[JobDescription]:
    return jd_service.get_all_jds()


@router.get("/jd/{jd_id}", response_model=JobDescription)
def get_jd(jd_id: str) -> JobDescription:
    jd = jd_service.get_jd(jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="JD not found")
    return jd


@router.post("/jd", response_model=JobDescription)
def create_jd(jd: JobDescription) -> JobDescription:
    return jd_service.save_jd(jd)


@router.put("/jd/{jd_id}", response_model=JobDescription)
def update_jd(jd_id: str, jd: JobDescription) -> JobDescription:
    jd.id = jd_id
    return jd_service.save_jd(jd)


@router.delete("/jd/{jd_id}")
def delete_jd(jd_id: str) -> dict[str, bool]:
    success = jd_service.delete_jd(jd_id)
    if not success:
        raise HTTPException(status_code=404, detail="JD not found")
    return {"success": True}


# ===== JD 解析 =====

class JDParseRequest(BaseModel):
    text: str


class JDParseResponse(BaseModel):
    title: str
    company: str
    location: str
    skills: list[str]
    description: str
    requirements: str
    responsibilities: list[str]


@router.post("/jd/parse", response_model=JDParseResponse)
def parse_jd(request: JDParseRequest) -> JDParseResponse:
    result = jd_service.parse_jd_text(request.text)
    return JDParseResponse(**result)


# ===== 匹配分析 =====

@router.get("/jd/{jd_id}/match", response_model=MatchResult)
def match_analysis(jd_id: str) -> MatchResult:
    result = jd_service.match_analysis(jd_id)
    if not result:
        raise HTTPException(status_code=404, detail="JD not found")
    return result


# ===== 猎聘 MCP 职位搜索 =====

class JobSearchResponse(BaseModel):
    items: list[LiepinJobItem]
    total: int = 0
    page: int = 1
    page_size: int = 20
    source: str = "liepin_mcp"


@router.get("/jobs/search", response_model=JobSearchResponse)
async def search_external_jobs(
    keyword: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=50, description="每页数量"),
) -> JobSearchResponse:
    """通过猎聘 MCP 搜索外部职位"""
    items = await liepin_service.search_jobs(
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return JobSearchResponse(
        items=items,
        total=len(items),
        page=page,
        page_size=page_size,
        source="liepin_mcp" if liepin_service.is_available else "mock",
    )


@router.get("/jobs/external/status")
def check_external_status() -> dict[str, Any]:
    """检查猎聘 MCP 连接状态"""
    return {
        "available": liepin_service.is_available,
        "source": "liepin_mcp" if liepin_service.is_available else "mock",
        "note": "猎聘 MCP: 国内首个支持 AI Agent 接入的招聘平台" if liepin_service.is_available else "使用模拟数据。安装 liepin-mcp 后可接入真实数据",
    }


class JobDetailRequest(BaseModel):
    job_id: str


@router.get("/jobs/external/{job_id}")
async def get_external_job_detail(job_id: str) -> dict[str, Any]:
    """获取猎聘职位详情"""
    detail = await liepin_service.get_job_detail(job_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Job not found")
    return detail.model_dump()


class ImportJobRequest(BaseModel):
    job_id: str
    title: str
    company: str
    location: str = ""
    salary: str = ""
    description: str = ""
    requirements: str = ""
    skills: list[str] = []
    responsibilities: list[str] = []
    experience: str = ""
    education: str = ""
    industry: str = ""
    job_type: str = ""


@router.post("/jobs/import", response_model=JobDescription)
def import_external_job(request: ImportJobRequest) -> JobDescription:
    """将猎聘职位导入到本地岗位库"""
    jd = JobDescription(
        title=request.title,
        company=request.company,
        location=request.location,
        salary=request.salary,
        experience=request.experience,
        education=request.education,
        industry=request.industry,
        job_type=request.job_type,
        description=request.description,
        requirements=request.requirements,
        skills=request.skills,
        responsibilities=request.responsibilities,
    )
    return jd_service.save_jd(jd)
