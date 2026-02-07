from typing import AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from uuid import UUID

from app.core.config import settings
from app.domain.schemas.token import TokenData
from app.domain.schemas.user import UserRole
from app.core.exceptions import CredentialsException, KairosException

from app.services.schedule_service import ScheduleService 
from app.domain.interfaces import AIBrain, ImageProcessor, VectorRepository, UserRepository, TokenRepository, CacheRepository

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.repositories.schedule import SQLAlchemyScheduleRepository
from app.infrastructure.db.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.ai.vector_repository import PGVectorRepository
from app.infrastructure.ai.brain import FakeBrain, GeminiBrain
from app.infrastructure.ai.image_processor import GeminiImageProcessor

from app.infrastructure.redis.token_repository import RedisTokenRepository
from app.infrastructure.redis.cache_repository import RedisCacheRepository

from app.services.chat_service import ChatService
from app.services.auth_service import AuthService
from app.services.user_service import UserService

#OAuth2 스키마 및 로그인 처리 API 주소
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 전역 변수로 인스턴스 캐싱
_vector_repo_instance = None
_token_repo_instance = None
_cache_repo_instance = None

# `ScheduleService`를 만들려면 `repo`가 필요하고 `repo`를 만들려면 `db`가 필요하므로 순서대로 조립하여 완성품 만듭니다.
# DB 세션 생성
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Repository 주입 (Session 필요)
def get_schedule_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyScheduleRepository:
    return SQLAlchemyScheduleRepository(db)

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db) # SQLAchemy 구현체 반환

def get_user_service(
        repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo)

def get_toekn_repository() -> TokenRepository:
    global _token_repo_instance
    if _token_repo_instance is None:
        _token_repo_instance = RedisTokenRepository()
    return _token_repo_instance

def get_cache_repository() -> CacheRepository:
    global _cache_repo_instance
    if _cache_repo_instance is None:
        _cache_repo_instance = RedisCacheRepository()
    return _cache_repo_instance

def get_image_processor() -> ImageProcessor:
    return GeminiImageProcessor()

# [임시] 개발용 Mock 유저 ID
TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

def get_auth_servcie(token_repo: TokenRepository = Depends(get_toekn_repository)) -> AuthService:
    return AuthService(token_repo)

async def get_current_user_id(token: str = Depends(oauth2_schema),
                        token_repo: TokenRepository = Depends(get_toekn_repository)) -> UUID:
    """
    HTTP 요청 헤더(Authorization: Bearer <Token>)에서 토큰을 꺼내 검증하고
    그 안에 들어 있는 user_id를 반환합니다.
    """
    if await token_repo.is_blacklisted(token):
        raise CredentialsException()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise CredentialsException()

        token_data = TokenData(user_id=user_id_str)
    
    except JWTError:
        raise ConnectionError()

    return UUID(token_data.user_id)

# Repository 주입 (Session 불필요)
def get_vector_repository() -> PGVectorRepository:
    global _vector_repo_instance
    if _vector_repo_instance is None:
        print("Initializing PGVector Repository")
        try:
            _vector_repo_instance = PGVectorRepository()
        except Exception as e:
            print(f"Error initializing PGVector Repo: {e}")
            raise e
    return _vector_repo_instance

# Service 주입 (Repository 필요)
def get_schedule_service(
        repo: SQLAlchemyScheduleRepository = Depends(get_schedule_repository),
        vector_repo: VectorRepository = Depends(get_vector_repository),
        image_processor: ImageProcessor = Depends(get_image_processor),
        cache_repo: CacheRepository = Depends(get_cache_repository)
) -> ScheduleService:
    return ScheduleService(repo, vector_repo, image_processor, cache_repo)

def get_ai_brain() -> AIBrain:
    return GeminiBrain()

def get_chat_service(
        vector_repo: VectorRepository = Depends(get_vector_repository),
        brain: AIBrain = Depends(get_ai_brain)
) -> ChatService:
    return ChatService(vector_repo, brain)

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(oauth2_schema)):
        """
        토큰 안에 있는 role이 허용된 목록에 있는지 확인
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            role_str = payload.get("role")

            if role_str is None:
                raise CredentialsException()
            
            if role_str not in [r.value for r in self.allowed_roles]:
                raise KairosException(
                    message="권한이 부족합니다.",
                    code="PERMISSION-DENIED",
                    status_code=403
                )
        except JWTError:
            raise CredentialsException()
            
# 관리자용 의존성 인스턴스
allowed_roles_only = RoleChecker([UserRole.ADMIN])