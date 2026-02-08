from uuid import UUID

from app.domain.interfaces import AIBrain, VectorRepository
from app.domain.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self, vector_repo: VectorRepository, brain: AIBrain):
        self.vector_repo = vector_repo
        self.brain = brain

    async def chat(self, user_id: UUID, request: ChatRequest) -> ChatResponse:
        # Retrieval 구현: 사용자 질문과 관련된 과거 기억(일정) 검색
        relevant_docs = await self.vector_repo.search(
            query=request.message, user_id=user_id, limit=3
        )

        # Context 구현: 검색된 일정 통합
        if relevant_docs:
            context_str = "\n".join([f"- {doc}" for doc in relevant_docs])
        else:
            context_str = "관련된 과거 일정이 없습니다."

        # Generation 구현: 질문+맥락 전달
        answer = await self.brain.ask(question=request.message, context=context_str)

        return ChatResponse(answer=answer)
