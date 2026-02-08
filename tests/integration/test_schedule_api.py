import pytest
from unittest.mock import patch
from app.core.security import create_access_token

# 시나리오
# 1. 로그인 (토큰 발급)
# 2. 일정 생성 API 호출 (POST)
# 3. 201 응답 확인
# 4. Celery Task 호출 여부 확인

@pytest.mark.asyncio
async def test_create_schedule_api(client, db_session):
    test_user_id = "test1@example.com"

    access_token = create_access_token(subject=test_user_id)
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "title": "통합 테스트 일정2",
        "description": "API 엔트포인트 테스트 중2",
        "type": "TASK",
        "dealine": "2026-12-31T23:59:59",
    }

    with patch("app.services.schedule_service.task_save_vector.delay") as mock_celery:
        response = await client.post(
            "/api/v1/schedules/",
            json=payload,
            headers=headers,
        )

        assert response.status_code==201, f"Response: {response.text}"

        data = response.json()
        assert data["title"] == payload["title"]
        assert data["type"] == "TASK"

        mock_celery.assert_called_once()