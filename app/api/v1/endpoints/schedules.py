from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from app.api.dependencies import get_current_user_id, get_schedule_service
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services.schedule_service import ScheduleService

router = APIRouter()


@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새 일정 생성",
)
async def create_schedule(
    schedule_in: ScheduleCreate,
    background_tasks: BackgroundTasks,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    새로운 일정(Event/Task)를 생성
    """
    return await service.create_schedule(schedule_in, user_id, background_tasks)

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="일정 삭제")
async def delete_schedule(
    schedule_id: UUID,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """특정 일정을 삭제합니다."""
    await service.delete_schedule(schedule_id, user_id)
    return

@router.get("/", response_model=List[ScheduleResponse], summary="내 일정 목록 조회")
async def read_schedules(
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    현재 사용자의 모든 일정을 조회
    """
    return await service.get_schedules(user_id)


@router.patch("/{schedule_id}", response_model=ScheduleResponse, summary="일정 수정")
async def update_schedule(
    schedule_id: UUID,
    schedule_in: ScheduleUpdate,
    background_tasks: BackgroundTasks,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    일정의 일부 정보를 수정
    수정 시 과거 이력이 자동으로 저장
    """
    return await service.update_schedule(
        schedule_id, schedule_in, user_id, background_tasks
    )


@router.get("/search", summary="자연어 일정 검색 (Vector Search)")
async def search_schedules(
    query: str,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    'A 프로젝트는 언제까지야?"와 같이 자연어로 질문하면
    의미상 유사한 과거 일정을 벡터 DB에서 찾아 반환
    """

    return await service.search_schedules(query, user_id)


@router.post(
    "/image", response_model=List[ScheduleResponse], summary="이미지로 일정 등록 (OCR)"
)
async def create_schedule_by_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    servcie: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    이미지 파일(청첩장, 시간표 등)을 업로드하면 내용을 분석하여 다중 일정을 자동 등록
    """
    contents = await file.read()

    return await servcie.create_schedule_from_image(
        image_bytes=contents,
        mime_type=file.content_type,
        user_id=user_id,
        background_tasks=background_tasks,
    )
