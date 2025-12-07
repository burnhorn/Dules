from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services.schedule_service import ScheduleService
from app.api.dependencies import get_schedule_service, get_current_user_id

router = APIRouter()

@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새 일정 생성"
)
async def create_schedule(
    schedule_in: ScheduleCreate,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    새로운 일정(Event/Task)를 생성합니다.
    
    :param schedule_in: EVENT(시간 확정 일정) 또는 TASK(마감 기반 일정)
    :type schedule_in: ScheduleCreate
    :param service: 비즈니스 로직
    :type service: ScheduleService
    :param user_id: 현재 로그인한 유저 ID
    :type user_id: UUID
    """
    return await service.create_schedule(schedule_in, user_id)


@router.get(
    "/",
    response_model=List[ScheduleResponse],
    summary="내 일정 목록 조회"
)
async def read_schedules(
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    현재 사용자의 모든 일정을 조회합니다.

    :param service: 비즈니스 로직
    :type service: ScheduleService
    :param user_id: 현재 로그인한 유저 ID
    :type user_id: UUID
    """
    return await service.get_schedules(user_id)


@router.patch(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="일정 수정"
)
async def update_schedule(
    schedule_id: UUID,
    schedule_in: ScheduleUpdate,
    service: ScheduleService = Depends(get_schedule_service),
    user_id: UUID = Depends(get_current_user_id)
):
    """
    일정의 일부 정보를 수정합니다.
    수정 시 과거 이력이 자동으로 저장됩니다.
    
    :param schedule_id: 일정 식별값
    :type schedule_id: UUID
    :param schedule_in: 수정할 일정 정보
    :type schedule_in: ScheduleUpdate
    :param service: 비즈니스 로직
    :type service: ScheduleService
    :param user_id: 현재 로그인한 유저 ID
    :type user_id: UUID
    """
    return await service.update_schedule(schedule_id, schedule_in, user_id)