from fastapi import BackgroundTasks, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import pytz

from app.domain.interfaces import ScheduleRepository, VectorRepository, ImageProcessor
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.infrastructure.db.models.schedule import ScheduleHistory

class ScheduleService:
    """
    일정 로직의 순서와 규칙(트랜잭션)을 보장
    """
    def __init__(self, repo: ScheduleRepository, vector_repo: VectorRepository, image_processor: ImageProcessor):
        self.repo = repo
        self.vector_repo = vector_repo
        self.image_processor = image_processor

    async def create_schedule(self,
                              data: ScheduleCreate,
                              user_id: UUID,
                              background_taks: BackgroundTasks
                              ) -> ScheduleResponse:
        # DB 저장 요청 (빠름)
        created_schedule = await self.repo.create(data, user_id)

        # 백터 DB 저장 (느림)
        text_to_embed = f"일정: {created_schedule.title}\n내용: {created_schedule.description or '없음'}"

        background_taks.add_task(
            self.vector_repo.save,
            text=text_to_embed,
            user_id=user_id,
            metadata={"schedule_id": str(created_schedule.id)}
        )
        
        # 응답 반환 (ORM 객체 -> Pydantic Schema)
        return ScheduleResponse.model_validate(created_schedule)
    
    async def get_schedules(self, user_id: UUID) -> List[ScheduleResponse]:
        schedules = await self.repo.get_all_by_user(user_id)
        return [ScheduleResponse.model_validate(s) for s in schedules]
    
    async def update_schedule(
            self,
            schedule_id: UUID,
            update_date: ScheduleUpdate,
            user_id: UUID,
            background_tasks: BackgroundTasks
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

        # 벡터 데이터 업데이트
        if update_date.title or update_date.description:
            text_to_embed = f"일정: {schedule.title}\n내용:{schedule.description or '없음'}"
            background_tasks.add_task(
                self.vector_repo.save,
                text=text_to_embed,
                user_id=user_id,
                metadata={"schedule_id": str(schedule.id)}
            )

        return ScheduleResponse.model_validate(schedule)

    async def search_schedules(self, query: str, user_id: UUID) -> List[str]:
        """
        백터 DB에서 질문(query)과 유사한 일정 내용을 검색합니다.
        """
        results = await self.vector_repo.search(query=query, user_id=user_id, limit=5)

        if not results:
            return ["관련된 과거 일정을 찾을 수 없습니다."]
        
        return results
    
    async def create_schedule_from_image(
            self,
            image_bytes: bytes,
            mime_type: str,
            user_id: UUID,
            background_tasks: BackgroundTasks
    ) -> ScheduleResponse:
        
        kst = pytz.timezone("Asia/Seoul")
        now_kst = datetime.now(kst)

        schedule_data = await self.image_processor.extract_schedule(
            image_bytes, mime_type, now_kst
            )
        
        # DRY 원칙: 기존의 메서드 활용하여 DB 저장
        return await self.create_schedule(schedule_data, user_id, background_tasks)