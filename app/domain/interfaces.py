from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Protocol
from uuid import UUID

# 런타임 시 미실행, IDE 시 실행
if TYPE_CHECKING:
    from app.domain.schemas.schedule import ScheduleCreate
    from app.infrastructure.db.models.schedule import Schedule, ScheduleHistory
    from app.infrastructure.db.models.user import User


class ScheduleRepository(Protocol):
    """
    일정 관리를 위한 저장소 인터페이스
    """

    async def create(self, schedule: "ScheduleCreate", user_id: UUID) -> "Schedule": ...

    async def get_by_id(self, schedule_id: UUID) -> Optional["Schedule"]: ...

    async def get_all_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List["Schedule"]: ...

    async def update(self, schedule: "Schedule") -> "Schedule": ...

    async def create_history(self, history: "ScheduleHistory") -> Any: ...

    async def commit(self) -> None: ...

    async def refresh(self, instance: Any) -> None: ...


class VectorRepository(Protocol):
    """
    텍스트 데이터를 벡터화하여 저장하고 검색하는 인터페이스
    """

    async def save(self, text: str, user_id: UUID, metadata: dict = None) -> None:
        """텍스트를 임베딩하여 저장 (user_id를 사용하여 본인의 것만 저장)"""
        ...

    async def search(self, query: str, user_id: UUID, limit: int = 3) -> List[str]:
        """유사한 텍스트 검색 (user_id를 사용하여 본인의 것만 검색)"""
        ...

    async def delete(self, doc_id: str) -> None:
        """특정 문서 삭제 (업데이트 시 필요)"""
        ...


class Llm(Protocol):
    """
    LLM과 통신을 담당하는 인터페이스
    """

    async def ask(self, question: str, context: str) -> str:
        """
        주어진 맥락(context)를 바탕으로 질문에 답변
        """
        ...


class ImageProcessor(Protocol):
    """
    이미지 파일을 분석하여 일정 정보를 추출하는 인터페이스
    """

    async def extract_schedule(
        self, image_bytes: bytes, mime_type: str, reference_date: datetime
    ) -> "ScheduleCreate": ...


class UserRepository(Protocol):
    """
    유저 정보를 관리하는 저장소 인터페이스
    """

    async def get_by_email(self, email: str, load_schedules: bool = False) -> Optional["User"]: ...

    async def create(self, user: "User", hashed_password: str) -> "User": ...

    async def commit(self) -> None: ...

    async def refresh(self, instance: Any) -> None: ...


class TokenRepository(Protocol):
    """
    인증 토큰(JWT)의 상태를 관리하는 저장소
    (Redis 구현체 교체용)
    """

    async def add_to_blacklist(self, token: str, expires_in: int) -> None:
        """
        토큰을 블랙리스트에 추가
        """
        ...

    async def is_blacklisted(self, token: str) -> bool:
        """
        토큰이 블랙리스트에 있는지 확인
        """
        ...

    async def close(self) -> None:
        """
        Redis 종료
        """
        ...

    async def save_refresh_token(
        self, token: str, user_id: UUID, expires_in: int
    ) -> None:
        """
        Refresh Token 저장
        """
        ...

    async def get_refresh_token_user_id(self, token: str) -> Optional[str]:
        """
        Refresh Token 검증(존재 여부 및 소유자 확인)
        """
        ...

    async def delete_refresh_token(self, token: str) -> None:
        """
        Refresh Token 삭제 (로그아웃용)
        """
        ...


class CacheRepository(Protocol):
    """
    데이터 캐싱을 담당하는 인터페이스
    """

    async def get(self, key: str) -> Optional[str]:
        """
        캐시 조회
        """
        ...

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """
        캐시 저장
        """
        ...

    async def delete(self, key: str) -> None:
        """
        캐시 삭제
        """
        ...

    async def delete_pattern(self, pattern: str) -> None:
        """
        특정 패턴의 키 일괄 삭제
        """
        ...
