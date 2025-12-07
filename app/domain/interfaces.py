from typing import Protocol, List, Optional, Any
from uuid import UUID
from datetime import datetime
from app.domain.schemas.schedule import ScheduleCreate, ScheduleType

class ScheduleRepository(Protocol):
    """
    일정 관리를 위한 저장소 인터페이스
    구체적인 DB 기술(SQLAlchemy 등)에 의존하지 않습니다.
    """
    async def create(self, schedule: ScheduleCreate, user_id: UUID) -> Any:
        ...

    async def get_by_id(self, schedule_id: UUID) -> Optional[Any]:
        ...

    async def get_all_by_user(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 100) -> List[object]:
        ...
    
    async def update(self, schedule: object) -> Any:
        ...
    
    async def create_history(self, history: object) -> Any:
        ...

    async def commit(self) -> None:
        ...

    async def refresh(self, instance: Any) -> None:
        ...

