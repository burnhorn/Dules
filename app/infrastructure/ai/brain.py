import asyncio
from app.domain.interfaces import AIBrain

class FakeBrain(AIBrain):
    """
    개발 및 테스트용 가짜 두뇌
    외부 API를 호출하지 않고 고정된 응답을 반환합니다.
    """
    async def ask(self, question: str, context: str) -> str:
        await asyncio.sleep(0.5)

        return (
            f"[Fake AI 답변]\n"
            f"질문하신 '{question}'에 대해 답변드립니다.\n"
            f"참고한 과거 일정 정보:\n{context or '없음'}"
        )
