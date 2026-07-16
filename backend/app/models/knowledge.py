"""Knowledge base data models."""

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """A document in the knowledge base."""

    id: str = ""
    title: str = ""
    content: str = ""
    source: str = ""
    chunk_count: int = 0


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(description="Search query")
    top_k: int = Field(default=5, description="Number of results")


class KnowledgeSearchResult(BaseModel):
    text: str
    score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]


class KnowledgeStatsResponse(BaseModel):
    document_count: int
    vector_dimension: int
    index_type: str


class UploadResponse(BaseModel):
    message: str
    chunks_added: int
    stats: KnowledgeStatsResponse
