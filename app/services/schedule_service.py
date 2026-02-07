from fastapi import BackgroundTasks, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import pytz
import json

from app.domain.interfaces import ScheduleRepository, VectorRepository, ImageProcessor, CacheRepository
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.infrastructure.db.models.schedule import ScheduleHistory
from app.core.exceptions import ResourceNotFoundException, KairosException
from app.worker import task_save_vector

class ScheduleService:
    """
    일정 로직의 순서와 규칙(트랜잭션)을 보장
    - 캐시 기능 추가
    """
    def __init__(
            self, 
            repo: ScheduleRepository, 
            vector_repo: VectorRepository, 
            image_processor: ImageProcessor, 
            cache_repo: CacheRepository
    ):
        self.repo = repo
        self.vector_repo = vector_repo
        self.image_processor = image_processor
        self.cache_repo = cache_repo

    async def create_schedule(self,
                              data: ScheduleCreate,
                              user_id: UUID,
                              background_taks: BackgroundTasks
                              ) -> ScheduleResponse:
        # 캐시 삭제
        await self._invalidate_cache(user_id)

        # DB 객체 생성 및 세션 등록 (Insert 준비)
        created_schedule = await self.repo.create(data, user_id)

        # 트랜젝션 확정 / (다른 로직 수행 가능)
        await self.repo.commit()

        # 갱신된 DB 값 가져오기
        await self.repo.refresh(created_schedule)

        # 백터 DB 저장
        text_to_embed = f"일정: {created_schedule.title}\n내용: {created_schedule.description or '없음'}"

        task_save_vector.delay(
            text=text_to_embed,
            user_id=str(user_id),
            schedule_id=str(created_schedule.id)
        )
        
        # 응답 반환 (ORM 객체 -> Pydantic Schema)
        return ScheduleResponse.model_validate(created_schedule)
    
    async def get_schedules(self, user_id: UUID) -> List[ScheduleResponse]:
        cache_key = f"schedules:user:{user_id}"

        # Cache Hit Case
        cached_data = await self.cache_repo.get(cache_key)
        if cached_data:
            print("[Cache] Redis에서 일정 목록 반환")
            data_list = json.loads(cached_data)
            return [ScheduleResponse(**item) for item in data_list]
        
        # Cache Miss Case
        print("[DB] 데이터베이스 조회 중...")
        schedules = await self.repo.get_all_by_user(user_id)
        response = [ScheduleResponse.model_validate(s) for s in schedules]

        # Serialization
        json_str = json.dumps([r.model_dump(mode='json') for r in response])
        await self.cache_repo.set(cache_key, json_str, ttl=300)

        return response
    
    async def _invalidate_cache(self, user_id: UUID):
        """
        Cache Invalidation (Create, Update 시 활용)
        """
        cache_key = f"schedules:user:{user_id}"
        await self.cache_repo.delete(cache_key)
        print(f"[Cache] 캐시 삭제 완료: {cache_key}")

    async def update_schedule(
            self,
            schedule_id: UUID,
            update_date: ScheduleUpdate,
            user_id: UUID,
            background_tasks: BackgroundTasks
    ) -> ScheduleResponse:
        # 캐시 삭제
        await self._invalidate_cache(user_id)

        # 기존 일정 조회 (없으면 404)
        schedule = await self.repo.get_by_id(schedule_id)
        if not schedule:
            raise ResourceNotFoundException(resource="일정")
        
        # 보안요소: 내 일정이 맞는지 확인
        if schedule.user_id != user_id:
            raise KairosException(
                message="수정 권한이 없습니다.",
                code="PERMISSION_DENIED",
                status_code=403
            )
        
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