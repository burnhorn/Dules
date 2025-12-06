from typing import List, Optional
from uuid import UUID

from app.domain.interfaces import ScheduleRepository
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse

class ScheduleService:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    async def create_schedule(self, data: ScheduleCreate, user_id: UUID) -> ScheduleResponse:
        # 비즈니스 로직 (중복 일정 체크, AI 조언 요청)
        await self.check_conflict(data)

        # 저장 요청
        created_schedule = await self.repo.create(data, user_id)

        # 응답 반환 (ORM 객체 -> Pydantic Schema)
        return ScheduleResponse.model_validate(created_schedule)
    
    async def get_schedules(self, user_id: UUID) -> List[ScheduleResponse]:
        schedules = await self.repo.get_all_by_user(user_id)
        return [ScheduleResponse.model_validate(s) for s in schedules]