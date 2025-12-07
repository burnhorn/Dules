from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.interfaces import ScheduleRepository
from app.domain.schemas.schedule import ScheduleCreate
from app.infrastructure.db.models import Schedule

class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, schedule_data: ScheduleCreate, user_id: UUID) -> Schedule:
        # Pydantic 모델 => SQLAlchemy 모델 변환
        # exclude_unset=True: 클라이언트가 보내지 않은 값은 DB Default 값 사용
        db_schedule = Schedule(
            **schedule_data.model_dump(exclude_unset=True),
            user_id=user_id
        )
        self.db.add(db_schedule)
        await self.db.commit()
        await self.db.refresh(db_schedule)
        return db_schedule
    
    async def get_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        query = select(Schedule).where(Schedule.id == schedule_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_all_by_user(
            self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Schedule]:
        query = (
            select(Schedule)
            .where(Schedule.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()