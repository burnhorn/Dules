import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.schedule_service import ScheduleService
from app.domain.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleType
from app.infrastructure.db.models.schedule import Schedule


@patch("app.services.schedule_service.task_save_vector.delay")
async def test_create_schedule_success(
    mock_task_delay,
    mock_schedule_repo,
    mock_vector_repo,
    mock_image_processor,
    mock_cache_repo,
):
    """
    [시나리오] 정상적인 일정 생성 요청이 들어왔을 때:
    1. DB 저장(create)이 호출되어야 한다.
    2. 트랜잭션 확정(commit)이 호출되어야 한다.
    3. 벡터 저장(Celery)이 요청되어야 한다.
    """

    service = ScheduleService(
        repo=mock_schedule_repo,
        vector_repo=mock_vector_repo,
        image_processor=mock_image_processor,
        cache_repo=mock_cache_repo,
    )

    user_id = uuid4()
    schedule_data = ScheduleCreate(
        title="테스트 일정",
        type=ScheduleType.TASK,
        deadline=datetime.now()
    )

    mock_created_shcedule = Schedule(
        id=uuid4(),
        user_id=user_id,
        title=schedule_data.title,
        type=schedule_data.type,
        created_at=datetime.now()
    )

    mock_schedule_repo.create.return_value = mock_created_shcedule

    mock_background_tasks = MagicMock()

    result = await service.create_schedule(
        data=schedule_data,
        user_id=user_id,
        background_taks=mock_background_tasks,
    )

    assert isinstance(result, ScheduleResponse)
    assert result.title == "테스트 일정"

    mock_schedule_repo.create.assert_called_once()
    mock_schedule_repo.commit.assert_called_once()
    mock_schedule_repo.refresh.assert_called_once()
    mock_task_delay.assert_called_once()

    mock_cache_repo.delete.assert_called()