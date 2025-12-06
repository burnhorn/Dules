from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.repositories.schedule import SQLAlchemyScheduleRepository
from app.services.schedule_service import ScheduleService

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