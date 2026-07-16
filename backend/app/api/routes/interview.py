from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.services.interview_service import InterviewService

router = APIRouter()
interview_service = InterviewService()


@router.post("/interview/generate")
def generate_interview_questions(
    jd_id: Optional[str] = None,
    count: int = 15,
    categories: Optional[List[str]] = None,
):
    try:
        questions = interview_service.generate_questions(jd_id=jd_id, count=count, categories=categories)
        return {
            "questions": [q.to_dict() for q in questions],
            "count": len(questions),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成面试题失败: {str(e)}")


@router.get("/interview/categories")
def get_interview_categories():
    return {
        "categories": [
            {"id": "behavior", "name": "行为面试", "description": "考察候选人的工作态度、团队协作、抗压能力等"},
            {"id": "technical", "name": "技术面试", "description": "考察技术功底、算法能力、系统设计等"},
            {"id": "project", "name": "项目深挖", "description": "深入了解项目经历、技术决策、问题解决能力"},
            {"id": "comprehensive", "name": "综合能力", "description": "考察沟通能力、学习能力、职业规划等"},
        ]
    }