import asyncio
from uuid import UUID

from app.core.celery_app import celery_app
from app.infrastructure.ai.vector_repository import PGVectorRepository


async def _save_vector_async(text: str, user_id: UUID, schedule_id: str):
    """
    실제 비동기 로직
    """
    vector_repo = PGVectorRepository()
    await vector_repo.save(
        text=text, user_id=user_id, metadata={"schedule_id": schedule_id}
    )


@celery_app.task(acks_late=True)
def task_save_vector(text: str, user_id: str, schedule_id: str):
    try:
        user_id = UUID(user_id)

        asyncio.run(
            _save_vector_async(text=text, user_id=user_id, schedule_id=schedule_id)
        )

        return f"Saved vector for schedule {schedule_id}"

    except Exception as e:
        raise e
