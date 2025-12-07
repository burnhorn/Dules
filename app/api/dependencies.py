from typing import AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.repositories.schedule import SQLAlchemyScheduleRepository
from app.services.schedule_service import ScheduleService

# `ScheduleService`를 만들려면 `repo`가 필요하고 `repo`를 만들려면 `db`가 필요하므로 순서대로 조립하여 완성품 만듭니다.
# DB 세션 생성
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Repository 주입 (Session 필요)
def get_schedule_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyScheduleRepository:
    return SQLAlchemyScheduleRepository(db)

# Service 주입 (Repository 필요)
def get_schedule_service(
        repo: SQLAlchemyScheduleRepository = Depends(get_schedule_repository)
) -> ScheduleService:
    return ScheduleService(repo)

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