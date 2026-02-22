from functools import lru_cache
from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import CredentialsException, DulesException

# =================================================================
# Interface
# =================================================================
from app.domain.interfaces import (
    Llm,
    CacheRepository,
    ImageProcessor,
    ScheduleRepository,
    TokenRepository,
    UserRepository,
    VectorRepository,
)
from app.domain.schemas.token import TokenData
from app.domain.schemas.user import UserRole

# =================================================================
# Implementations
# =================================================================
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.redis.cache_repository import RedisCacheRepository
from app.infrastructure.redis.token_repository import RedisTokenRepository

from app.infrastructure.ai.llm import GeminiLlm
from app.infrastructure.ai.image_processor import GeminiImageProcessor
from app.infrastructure.ai.vector_repository import PGVectorRepository
from app.infrastructure.db.repositories.schedule import SQLAlchemyScheduleRepository
from app.infrastructure.db.repositories.user import SQLAlchemyUserRepository

# =================================================================
# Services
# =================================================================
from app.services.chat_service import ChatService
from app.services.schedule_service import ScheduleService
from app.services.auth_service import AuthService
from app.services.user_service import UserService


# =================================================================
# Database Session
# =================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# =================================================================
# Infrastructure Singletons
# =================================================================
@lru_cache
def get_vector_repository() -> VectorRepository:
    print("Initializing PGVector Repository (Singleton)")
    return PGVectorRepository()


@lru_cache
def get_image_processor() -> ImageProcessor:
    return GeminiImageProcessor()


@lru_cache
def get_ai_llm() -> Llm:
    return GeminiLlm()


@lru_cache
def get_token_repository() -> TokenRepository:
    return RedisTokenRepository()


@lru_cache
def get_cache_repository() -> CacheRepository:
    return RedisCacheRepository()


# =================================================================
# Repository Factories
# =================================================================
def get_schedule_repository(
    db: AsyncSession = Depends(get_db),
) -> ScheduleRepository:
    return SQLAlchemyScheduleRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db)


# =================================================================
# Service Factories
# =================================================================
def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)


def get_auth_service(
    token_repo: TokenRepository = Depends(get_token_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(token_repo, user_repo)


def get_schedule_service(
    repo: SQLAlchemyScheduleRepository = Depends(get_schedule_repository),
    vector_repo: VectorRepository = Depends(get_vector_repository),
    image_processor: ImageProcessor = Depends(get_image_processor),
    cache_repo: CacheRepository = Depends(get_cache_repository),
) -> ScheduleService:
    return ScheduleService(repo, vector_repo, image_processor, cache_repo)


def get_chat_service(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    llm: Llm = Depends(get_ai_llm),
) -> ChatService:
    return ChatService(vector_repo, llm)


# =================================================================
# Security Dependencies
# =================================================================
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    token: str = Depends(oauth2_schema),
    token_repo: TokenRepository = Depends(get_token_repository),
) -> UUID:
    """
    HTTP 요청 헤더(Authorization: Bearer <Token>)에서 토큰을 꺼내 검증하고
    그 안에 들어 있는 user_id를 반환합니다.
    """
    if await token_repo.is_blacklisted(token):
        raise CredentialsException()

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise CredentialsException()

        token_data = TokenData(user_id=user_id_str)

    except JWTError:
        raise ConnectionError()

    return UUID(token_data.user_id)


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(oauth2_schema)):
        """
        토큰 안에 있는 role이 허용된 목록에 있는지 확인
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            role_str = payload.get("role")

            if role_str is None:
                raise CredentialsException()

            if role_str not in [r.value for r in self.allowed_roles]:
                raise DulesException(
                    message="권한이 부족합니다.",
                    code="PERMISSION-DENIED",
                    status_code=403,
                )
        except JWTError:
            raise CredentialsException()


# 관리자용 의존성 인스턴스
allowed_roles_only = RoleChecker([UserRole.ADMIN])
