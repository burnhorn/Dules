from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID

from app.domain.interfaces import ScheduleRepository
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.infrastructure.db.models.schedule import ScheduleHistory

class ScheduleService:
    """
    일정 로직의 순서와 규칙(트랜잭션)을 보장
    """
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    async def create_schedule(self, data: ScheduleCreate, user_id: UUID) -> ScheduleResponse:
        # 비즈니스 로직 (중복 일정 체크, AI 조언 요청)
        # await self.check_constraints(data)

        # 저장 요청
        created_schedule = await self.repo.create(data, user_id)

        # 응답 반환 (ORM 객체 -> Pydantic Schema)
        return ScheduleResponse.model_validate(created_schedule)
    
    async def get_schedules(self, user_id: UUID) -> List[ScheduleResponse]:
        schedules = await self.repo.get_all_by_user(user_id)
        return [ScheduleResponse.model_validate(s) for s in schedules]
    
    async def update_schedule(
            self,
            schedule_id: UUID,
            update_date: ScheduleUpdate,
            user_id: UUID
    ) -> ScheduleResponse:
        
        # 기존 일정 조회 (없으면 404)
        schedule = await self.repo.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
        # 보안요소: 내 일정이 맞는지 확인
        if schedule.user_id != user_id:
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
        
        # 이력(history) 기록 (변경 전 상태 스냅샷)
        history = ScheduleHistory(
            schedule_id = schedule.id,
            previous_title = schedule.title,
            previous_start_at = schedule.start_at,
            previous_end_at = schedule.end_at
        )
        await self.repo.create_history(history)

        # 데이터 업데이트 (Pydantc -> ORM): 값이 있는 것만 추출
        update_dict = update_date.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(schedule, key, value) # 객체 속성 덮어쓰기

        await self.repo.update(schedule)

        await self.repo.commit()
        await self.repo.refresh(schedule)

        return ScheduleResponse.model_validate(schedule)
