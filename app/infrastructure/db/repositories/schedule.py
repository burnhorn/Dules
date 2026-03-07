from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.domain.interfaces import ScheduleRepository
from app.domain.schemas.schedule import ScheduleCreate
from app.infrastructure.db.models.schedule import Schedule, ScheduleHistory


class SQLAlchemyScheduleRepository(ScheduleRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, schedule_data: ScheduleCreate, user_id: UUID) -> Schedule:
        # Pydantic 모델 => SQLAlchemy 모델 변환
        # exclude_unset=True: 클라이언트가 보내지 않은 값은 DB Default 값 사용
        db_schedule = Schedule(
            **schedule_data.model_dump(exclude_unset=True), user_id=user_id
        )
        self.db.add(db_schedule)

        return db_schedule

    async def get_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        query = (
            select(Schedule)
            .where(Schedule.id == schedule_id)
            .options(joinedload(Schedule.user)) 
            .options(selectinload(Schedule.histories)) 
        )
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

    async def search_by_date_and_keyword(self, user_id, start_date = None, end_date = None, keyword = None) -> List[Schedule]:
    
        stmt = select(Schedule).where(Schedule.user_id == user_id)

        schedule_start = func.coalesce(Schedule.start_at, Schedule.deadline)
        schedule_end = func.coalesce(Schedule.end_at, Schedule.deadline, Schedule.start_at)

        if start_date:
            stmt = stmt.where(schedule_end >= start_date)

        if end_date:
            stmt = stmt.where(schedule_start <= end_date)

        if keyword:
            stmt = stmt.where(
                or_(
                    Schedule.title.ilike(f"%{keyword}%"),
                    Schedule.description.ilike(f"%{keyword}%")
                )
            )
        
        stmt = stmt.order_by(
            Schedule.start_at.asc().nulls_last(),
            Schedule.deadline.asc().nulls_last()
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_history(self, history: ScheduleHistory):
        self.db.add(history)

    async def update(self, schedule: Schedule) -> Schedule:
        """
        변경사항 반영 준비
        """
        self.db.add(schedule)
        return schedule

    async def delete(self, schedule: Schedule) -> None:
        await self.db.delete(schedule)

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance):
        await self.db.refresh(instance)
