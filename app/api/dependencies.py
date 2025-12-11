from typing import AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.repositories.schedule import SQLAlchemyScheduleRepository
from app.services.schedule_service import ScheduleService, VectorRepository
from app.infrastructure.ai.vector_repository import PGVectorRepository 
from app.domain.interfaces import AIBrain
from app.infrastructure.ai.brain import FakeBrain
from app.services.chat_service import ChatService

# 전역 변수로 인스턴스 캐싱
_vector_repo_instance = None

# `ScheduleService`를 만들려면 `repo`가 필요하고 `repo`를 만들려면 `db`가 필요하므로 순서대로 조립하여 완성품 만듭니다.
# DB 세션 생성
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Repository 주입 (Session 필요)
def get_schedule_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyScheduleRepository:
    return SQLAlchemyScheduleRepository(db)

# [임시] 개발용 Mock 유저 ID
TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

def get_current_user_id() -> UUID:
    """
    JWT 토큰 파싱 로직으로 대체되기 전
    테스트용으로 고정된 ID를 반환합니다.
    
    :return: user_id
    :rtype: UUID
    """
    return TEST_USER_ID

# Repository 주입 (Session 불필요)
def get_vector_repository() -> PGVectorRepository:
    global _vector_repo_instance
    if _vector_repo_instance is None:
        print("Initializing PGVector Repository")
        try:
            _vector_repo_instance = PGVectorRepository()
        except Exception as e:
            print(f"Error initializing PGVector Repo: {e}")
            raise e
    return _vector_repo_instance

# Service 주입 (Repository 필요)
def get_schedule_service(
        repo: SQLAlchemyScheduleRepository = Depends(get_schedule_repository),
        vector_repo: VectorRepository = Depends(get_vector_repository)
) -> ScheduleService:
    return ScheduleService(repo, vector_repo)

def get_ai_brain() -> AIBrain:
    return FakeBrain()

def get_chat_service(
        vector_repo: VectorRepository = Depends(get_vector_repository),
        brain: AIBrain = Depends(get_ai_brain)
) -> ChatService:
    return ChatService(vector_repo, brain)