from uuid import UUID
from fastapi import APIRouter, Depends
from app.api.dependencies import get_chat_service, get_current_user_id
from app.domain.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/", response_model=ChatResponse, summary="AI와 대화하기")
async def chat_with_ai(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    사용자의 질문을 받아 과거 일정(Vecotr DB)를 검색한 뒤 답변합니다.
    """
    return await service.chat(user_id, request)