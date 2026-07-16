from typing import Literal

from pydantic import BaseModel


ChatStage = Literal[
    "basic_info",
    "self_intro",
    "work_experience",
    "skills",
    "education",
    "project_experience",
    "awards",
    "self_evaluation",
]


class ChatStartResponse(BaseModel):
    session_id: str
    reply: str
    stage: ChatStage
    stage_label: str
    missing_info: list[str]
    should_summarize: bool
    summary_preview: str


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    stage: ChatStage


class ChatMessageResponse(BaseModel):
    reply: str
    stage: ChatStage
    stage_label: str
    missing_info: list[str]
    should_summarize: bool
    summary_preview: str