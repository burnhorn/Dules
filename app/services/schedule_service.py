import json
import structlog
import difflib
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import pytz
from fastapi import BackgroundTasks

from app.core.exceptions import DulesException, ResourceNotFoundException
from app.domain.interfaces import (
    CacheRepository,
    ImageProcessor,
    ScheduleRepository,
    VectorRepository,
)
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleType, ScheduleUpdate
from app.infrastructure.db.models.schedule import ScheduleHistory
from app.worker import task_save_vector

logger = structlog.get_logger()

class ScheduleService:
    """
    비즈니스 로직(순서 및 트랜잭션)
    - 캐시 기능 추가
    """

    def __init__(
        self,
        repo: ScheduleRepository,
        vector_repo: VectorRepository,
        image_processor: ImageProcessor,
        cache_repo: CacheRepository,
    ):
        self.repo = repo
        self.vector_repo = vector_repo
        self.image_processor = image_processor
        self.cache_repo = cache_repo

    async def create_schedule(
        self, data: ScheduleCreate, user_id: UUID, background_tasks: BackgroundTasks
    ) -> ScheduleResponse:

        await self._invalidate_cache(user_id)

        # RDB 저장
        created_schedule = await self.repo.create(data, user_id)
        await self.repo.commit()
        await self.repo.refresh(created_schedule)

        # 백터 DB 저장
        text_to_embed = f"일정: {created_schedule.title}\n내용: {created_schedule.description or '없음'}"

        task_save_vector.delay(
            text=text_to_embed,
            user_id=str(user_id),
            schedule_id=str(created_schedule.id),
        )

        return ScheduleResponse.model_validate(created_schedule)

    async def create_schedule_from_image(
        self, image_bytes: bytes, mime_type: str, user_id: UUID, background_tasks: BackgroundTasks,
    ) -> List[ScheduleResponse]:
        
        kst = pytz.timezone("Asia/Seoul")
        now_kst = datetime.now(kst)

        schedule_data_list = await self.image_processor.extract_schedule(
            image_bytes, mime_type, now_kst
        )

        existing_schedules = await self.repo.get_all_by_user(user_id, limit=50)
        skipped_count = 0

        created_schedules = []

        for new_schedule in schedule_data_list:
            is_duplicate = False

            for existing in existing_schedules:
                similarity = self._calculate_similarity(new_schedule.title, existing.title)

                if similarity >= 0.7:
                    # print(f"[Deduplication] 중복 스킵: '{new_schedule.title}' (유사도: {similarity*100:.1f}% -> 매칭: '{existing.title}')")
                    is_duplicate = True
                    break
            if is_duplicate:
                skipped_count += 1
                continue

            created = await self.create_schedule(new_schedule, user_id, background_tasks)
            created_schedules.append(created)
            
        # print(f"[ETL] 파이프라인 완료: 총 {len(schedule_data_list)}개 추출 -> {len(created_schedules)}개 저장 / {skipped_count}개 중복 스킵")
        return created_schedules

    async def delete_schedule(self, schedule_id: UUID, user_id: UUID) -> None:
        await self._invalidate_cache(user_id)

        schedule = await self.repo.get_by_id(schedule_id)
        if not schedule:
            raise ResourceNotFoundException(resource="일정")
        
        if schedule.user_id != user_id:
            raise DulesException(
                message="삭제 권한이 없습니다.",
                code="PERMISSION_DENIED",
                status_code=403
            )
        
        await self.repo.delete(schedule)
        await self.repo.commit()

    async def get_schedules(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100,
            schedule_type: Optional[str] = None,
            exclude_type: Optional[str] = None
            ) -> List[ScheduleResponse]:
        
        cache_key = f"schedules:user:{user_id}:type:{schedule_type}:ex:{exclude_type}:skip:{skip}:limit:{limit}"

        log = logger.bind(user_id=str(user_id))

        # Cache Hit Case
        cached_data = await self.cache_repo.get(cache_key)
        if cached_data:
            log.info("cache_hit", source="redis")
            data_list = json.loads(cached_data)
            return [ScheduleResponse(**item) for item in data_list]

        # Cache Miss Case
        log.info("cache_miss", source="db")
        schedules = await self.repo.get_all_by_user(
            user_id,
            skip=skip,
            limit=limit,
            schedule_type=ScheduleType[schedule_type] if schedule_type else None,
            exclude_type=exclude_type
            )
        response = [ScheduleResponse.model_validate(s) for s in schedules]

        # Serialization
        json_str = json.dumps([r.model_dump(mode="json") for r in response])
        await self.cache_repo.set(cache_key, json_str, ttl=300)

        return response

    async def _invalidate_cache(self, user_id: UUID):
        """
        Cache Invalidation (Create, Update, Delete 시 활용)
        유저와 관련된 모든 조건부 캐시(type, skip 등)을 일괄 삭제
        """
        pattern = f"schedules:user:{user_id}*"
        await self.cache_repo.delete_pattern(pattern)
        logger.info("[Cache] 유저 관련 모든 일정 캐시 무효화 완료", user_id=str(user_id))

    async def update_schedule(
        self,
        schedule_id: UUID,
        update_date: ScheduleUpdate,
        user_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> ScheduleResponse:
        await self._invalidate_cache(user_id)

        # 기존 일정 조회 (없으면 404)
        schedule = await self.repo.get_by_id(schedule_id)
        if not schedule:
            raise ResourceNotFoundException(resource="일정")

        # 보안요소: 내 일정이 맞는지 확인
        if schedule.user_id != user_id:
            raise DulesException(
                message="수정 권한이 없습니다.",
                code="PERMISSION_DENIED",
                status_code=403,
            )

        # 이력 기록 (변경 전 상태 스냅샷)
        history = ScheduleHistory(
            schedule_id=schedule.id,
            previous_title=schedule.title,
            previous_start_at=schedule.start_at,
            previous_end_at=schedule.end_at,
        )
        await self.repo.create_history(history)

        update_dict = update_date.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(schedule, key, value)

        await self.repo.update(schedule)

        await self.repo.commit()
        await self.repo.refresh(schedule)

        # 벡터 데이터 업데이트
        if update_date.title or update_date.description:
            text_to_embed = (
                f"일정: {schedule.title}\n내용:{schedule.description or '없음'}"
            )
            background_tasks.add_task(
                self.vector_repo.save,
                text=text_to_embed,
                user_id=user_id,
                metadata={"schedule_id": str(schedule.id)},
            )

        return ScheduleResponse.model_validate(schedule)

    async def search_schedules(self, query: str, user_id: UUID) -> List[str]:
        """
        백터 DB에서 질문(query)과 유사한 일정 내용을 검색
        """
        results = await self.vector_repo.search(query=query, user_id=user_id, limit=5)

        if not results:
            return ["관련된 과거 일정을 찾을 수 없습니다."]

        return results
    
    def _calculate_similarity(self, a: str, b: str) -> float:
        """
        두 문자열의 형태적 유사도를 0.0 ~ 1.0 사이로 반환 (공백 무시)
        예: '회의 일정 기록' vs '정기회의 기록' -> 1.0 (100%)
        """
        if not a or not b:
            return 0.0
        
        str_a = a.replace(" ", "").lower()
        str_b = b.replace(" ", "").lower()
        return difflib.SequenceMatcher(None, str_a, str_b).ratio()
