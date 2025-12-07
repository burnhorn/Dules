from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse
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
    :param service: DB 접근 인터페이스
    :type service: ScheduleService
    :param user_id: 현재 로그인한 유저
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

    :param service:  DB 접근 인터페이스
    :type service: ScheduleService
    :param user_id: 현재 로그인한 유저
    :type user_id: UUID
    """
    return await service.get_schedules(user_id)