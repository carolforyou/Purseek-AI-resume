"""Knowledge base API routes."""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List

from app.models.knowledge import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeStatsResponse,
    UploadResponse,
)
from app.services.knowledge_base import get_knowledge_base
from app.services.groq_service import GroqService

router = APIRouter()
kb = get_knowledge_base()
groq_service = GroqService()


@router.post("/kb/search", response_model=KnowledgeSearchResponse)
def search_kb(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    results = kb.search(request.query, k=request.top_k)
    return KnowledgeSearchResponse(
        query=request.query,
        results=[KnowledgeSearchResult(text=t, score=s) for t, s in results],
    )


@router.get("/kb/stats", response_model=KnowledgeStatsResponse)
def get_kb_stats() -> KnowledgeStatsResponse:
    stats = kb.get_stats()
    return KnowledgeStatsResponse(**stats)


@router.post("/kb/upload-text", response_model=UploadResponse)
async def upload_text(payload: dict) -> UploadResponse:
    text = payload.get("text", "")
    title = payload.get("title", "manual_entry")

    if not text.strip():
        return UploadResponse(
            message="No text provided",
            chunks_added=0,
            stats=KnowledgeStatsResponse(**kb.get_stats()),
        )

    chunks = kb.add_documents([text], source=title)

    stats = kb.get_stats()
    return UploadResponse(
        message=f"Added {title}: {chunks} chunks",
        chunks_added=chunks,
        stats=KnowledgeStatsResponse(**stats),
    )


@router.delete("/kb")
def clear_kb() -> dict:
    kb.delete_all()
    return {"message": "Knowledge base cleared", "stats": KnowledgeStatsResponse(**kb.get_stats())}


@router.post("/knowledge/upload")
async def upload_knowledge(files: List[UploadFile] = File(...)):
    total_chunks = 0
    
    for file in files:
        try:
            content = await file.read()
            text = content.decode("utf-8", errors="ignore")
            
            if file.filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(content)
            elif file.filename.lower().endswith((".docx", ".doc")):
                text = extract_text_from_docx(content)
            
            chunks = kb.add_documents([text], source=file.filename)
            total_chunks += chunks
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {str(e)}")
    
    stats = kb.get_stats()
    return {
        "data": {
            "chunk_count": total_chunks,
            "stats": stats,
        },
        "message": f"Successfully uploaded {len(files)} files, added {total_chunks} chunks",
    }


@router.post("/knowledge/query")
async def query_knowledge(request: dict):
    question = request.get("question", "")
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    
    results = kb.search(question, k=5)
    
    if not results:
        return {
            "data": {
                "answer": "抱歉，知识库中没有找到相关信息。",
                "sources": [],
            }
        }
    
    context = "\n\n".join([f"[来源{i+1}] {text}" for i, (text, _) in enumerate(results)])
    
    prompt = f"""基于以下知识库内容，回答用户的问题：

知识库内容：
{context}

用户问题：{question}

要求：
1. 回答必须基于知识库内容，不要编造信息
2. 如果知识库中没有相关信息，请明确说明
3. 回答要简洁明了，直接针对问题
4. 引用来源时标注来源编号
"""
    
    try:
        answer = groq_service.generate(prompt)
    except Exception:
        answer = "抱歉，AI服务暂时不可用，请稍后重试。"
    
    sources = [
        {"content": text[:100], "source": f"知识库片段{i+1}", "page": "未知"}
        for i, (text, _) in enumerate(results)
    ]
    
    return {
        "data": {
            "answer": answer,
            "sources": sources,
        }
    }


@router.get("/knowledge/stats")
def get_knowledge_stats():
    stats = kb.get_stats()
    return {
        "data": {
            "vector_count": stats.get("document_count", 0),
            **stats,
        }
    }


def extract_text_from_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception:
        return content.decode("utf-8", errors="ignore")


def extract_text_from_docx(content: bytes) -> str:
    try:
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        return "\n\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return content.decode("utf-8", errors="ignore")