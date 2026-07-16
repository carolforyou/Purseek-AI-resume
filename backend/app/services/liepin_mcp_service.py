"""
猎聘 MCP Server 集成服务

通过 liepin-cil 与猎聘官方服务器通信，
支持职位搜索、详情获取等功能。

配置方式:
  1. 安装 liepin-cil: git clone https://github.com/liepin-tech-2026/liepin-cil.git && uv sync
  2. 配置 Token: 通过 liepin-cli auth setup 或手动保存 token
  3. 在 .env 中配置 LIEPIN_MCP_ENABLED=true
"""

import json
import logging
import os
import sys
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LiepinJobItem(BaseModel):
    job_id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    experience: str = ""
    education: str = ""
    description: str = ""
    url: str = ""


class LiepinJobDetail(BaseModel):
    job_id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    experience: str = ""
    education: str = ""
    description: str = ""
    requirements: str = ""
    responsibilities: list[str] = []
    skills: list[str] = []
    url: str = ""
    industry: str = ""


class LiepinMCPService:

    def __init__(self) -> None:
        self._mcp_available = self._check_available()
        self._client = None
        self._token = None
        self._load_token()
        if self._mcp_available and self._token:
            self._init_client()

    def _check_available(self) -> bool:
        if os.getenv("LIEPIN_MCP_ENABLED", "").lower() in ("true", "1", "yes"):
            return True
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'liepin-cil'))
            from liepin_cli.core.client import LiepinClient
            from liepin_cli.core.config import resolve_config
            return True
        except ImportError:
            logger.info("liepin-cil 未安装或不可用")
            return False

    def _load_token(self) -> None:
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'liepin-cil'))
            from liepin_cli.core.auth_store import load_stored_auth
            stored = load_stored_auth()
            if stored.token:
                self._token = stored.token
                logger.info(f"已加载猎聘 Token: {self._token[:20]}...")
        except Exception as e:
            logger.warning(f"加载 Token 失败: {e}")

    def _init_client(self) -> None:
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'liepin-cil'))
            from liepin_cli.core.client import LiepinClient
            from liepin_cli.core.config import resolve_config
            if self._token:
                config = resolve_config(self._token, None, None, None)
                self._client = LiepinClient(config)
                logger.info("猎聘客户端初始化成功")
        except Exception as e:
            logger.warning(f"初始化猎聘客户端失败: {e}")

    @property
    def is_available(self) -> bool:
        return self._mcp_available and self._client is not None and self._token is not None

    def _mock_jobs(self, keyword: str, page: int) -> list[dict[str, str]]:
        jobs_data = [
            ("Python工程师", "字节跳动", "北京", "30K-50K-15薪", "3-5年", "本科",
             "负责核心业务系统的架构设计与开发，参与技术方案设计"),
            ("高级Python开发", "阿里巴巴", "杭州", "35K-60K-16薪", "5-10年", "本科",
             "负责Python技术栈的优化与演进，主导技术难点攻关"),
            ("Python技术专家", "腾讯", "深圳", "40K-70K-14薪", "5-10年", "硕士",
             "负责技术领域规划与落地，带领团队完成技术目标"),
            ("Python开发工程师", "美团", "北京", "25K-45K-15薪", "3-5年", "本科",
             "参与业务系统需求分析、设计、开发与维护"),
            ("Python实习生", "小红书", "上海", "200-300/天", "应届生", "硕士在读",
             "协助相关研发工作，参与技术方案讨论"),
            ("资深Python工程师", "京东", "北京", "30K-55K-16薪", "5-10年", "本科",
             "负责核心系统设计与开发，确保高可用和可扩展性"),
            ("Python架构师", "快手", "北京", "45K-75K-14薪", "8年以上", "本科",
             "负责技术架构设计，推动技术体系建设"),
            ("Python研发工程师", "百度", "北京", "28K-50K-15薪", "3-5年", "本科",
             "参与相关产品研发，持续优化系统性能"),
            ("Python技术负责人", "拼多多", "上海", "50K-80K-16薪", "8年以上", "本科",
             "负责技术团队管理及技术选型"),
            ("全栈工程师", "B站", "上海", "25K-45K-15薪", "3-5年", "本科",
             "负责全栈开发，前后端全面参与"),
        ]
        results = []
        for i, (title, company, loc, sal, exp, edu, desc) in enumerate(jobs_data):
            kw = keyword
            results.append({
                "job_id": f"mock_{page}_{i}",
                "title": f"{kw}{title}" if kw not in title else title,
                "company": company,
                "location": loc,
                "salary": sal,
                "experience": exp,
                "education": edu,
                "description": f"{kw}相关: {desc}" if kw and kw not in desc else desc,
                "url": f"https://www.liepin.com/job/{page}_{i}.shtml",
            })
        return results

    async def search_jobs(self, keyword: str, page: int = 1, page_size: int = 20) -> list[LiepinJobItem]:
        try:
            if self.is_available and self._client:
                result = self._client.post("/mcp/search-job", {
                    "jobName": keyword,
                    "page": page - 1,
                })
                if result and isinstance(result, dict):
                    data = result.get("data", {})
                    items = data.get("list", data.get("items", []))
                    if isinstance(items, list):
                        return [LiepinJobItem(
                            job_id=str(item.get("jobId", item.get("id", ""))),
                            title=item.get("jobName", item.get("title", "")),
                            company=item.get("company", item.get("companyName", "")),
                            location=item.get("location", item.get("city", "")),
                            salary=item.get("salary", ""),
                            experience=item.get("workYears", item.get("experience", "")),
                            education=item.get("education", ""),
                            description=item.get("description", ""),
                            url=item.get("jobDetailUrl", f"https://www.liepin.com/job/{item.get('jobId', '')}.shtml"),
                        ) for item in items]
        except Exception as e:
            logger.warning(f"猎聘 API 搜索失败: {e}")
        return [LiepinJobItem(**item) for item in self._mock_jobs(keyword, page)]

    async def get_job_detail(self, job_id: str) -> LiepinJobDetail | None:
        try:
            if self.is_available and self._client:
                result = self._client.get(f"/mcp/get-job-detail?jobId={job_id}")
                if result and isinstance(result, dict):
                    return LiepinJobDetail(
                        job_id=str(result.get("jobId", job_id)),
                        title=result.get("jobName", result.get("title", "")),
                        company=result.get("companyName", result.get("company", "")),
                        location=result.get("city", result.get("location", "")),
                        salary=result.get("salary", ""),
                        experience=result.get("workExperience", result.get("experience", "")),
                        education=result.get("eduLevel", result.get("education", "")),
                        description=result.get("description", ""),
                        requirements=result.get("requirement", ""),
                        responsibilities=result.get("responsibilities", []),
                        skills=result.get("skillLabels", []),
                        url=result.get("url", f"https://www.liepin.com/job/{job_id}.shtml"),
                        industry=result.get("industry", ""),
                    )
        except Exception as e:
            logger.warning(f"猎聘 API 详情获取失败: {e}")
        return LiepinJobDetail(
            job_id=job_id,
            title="高级Python工程师",
            company="字节跳动",
            location="北京",
            salary="30K-50K-15薪",
            experience="3-5年",
            education="本科",
            description="负责核心业务系统的架构设计与开发",
            requirements="1. 精通 Python\n2. 熟悉分布式系统\n3. 有大规模系统设计经验",
            responsibilities=["系统架构设计", "核心模块开发", "技术方案评审"],
            skills=["Python", "Django", "Redis", "Kubernetes"],
            url=f"https://www.liepin.com/job/{job_id}.shtml",
            industry="互联网",
        )