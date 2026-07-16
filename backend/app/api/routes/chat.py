from fastapi import APIRouter, HTTPException

from app.models.chat import ChatMessageRequest, ChatMessageResponse, ChatStartResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.get("/chat/sessions")
def list_sessions() -> list[dict]:
    return chat_service.get_all_sessions()


@router.post("/chat/session/{session_id}/resume", response_model=ChatStartResponse)
def resume_session(session_id: str) -> ChatStartResponse:
    result = chat_service.resume_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.post("/chat/start", response_model=ChatStartResponse)
def start_chat() -> ChatStartResponse:
    return chat_service.start_chat()


@router.delete("/chat/session/{session_id}")
def delete_session(session_id: str) -> dict[str, bool]:
    success = chat_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@router.post("/chat/message", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest) -> ChatMessageResponse:
    return chat_service.reply_to_message(session_id=request.session_id, stage=request.stage, message=request.message)