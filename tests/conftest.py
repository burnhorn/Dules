import pytest
import pytest_asyncio
from uuid import UUID
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.config import settings
from app.infrastructure.db.base import Base
from app.domain.interfaces import (
    ScheduleRepository,
    VectorRepository,
    ImageProcessor,
    CacheRepository
)
from app.api.dependencies import get_db, get_current_user_id, get_cache_repository, get_image_processor, get_vector_repository

@pytest.fixture
def mock_schedule_repo():
    repo = AsyncMock(spec=ScheduleRepository)
    return repo


@pytest.fixture
def mock_vector_repo():
    return AsyncMock(spec=VectorRepository)


@pytest.fixture
def mock_image_processor():
    return AsyncMock(spec=ImageProcessor)


@pytest.fixture
def mock_cache_repo():
    repo = AsyncMock(spec=CacheRepository)
    repo.delete.return_value = None
    return repo


test_engine = create_async_engine(settings.DATABASE_URL, echo=False)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    [핵심 패턴: Transaction Rollback]
    1. 연결(Connection)을 맺고 트랜잭션을 시작합니다.
    2. 세션(Session)을 만들 때 이 연결을 빌려줍니다.
    3. join_transaction_mode="create_savepoint" 설정을 통해
       앱 내부에서 session.commit()을 해도 진짜 DB 커밋이 아니라 세이브포인트만 생성합니다..
    4. 테스트가 끝나면 최상위 트랜잭션을 롤백(rollback)하여 모든 데이터를 날립니다.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False
    )

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def client(
    db_session,
    mock_cache_repo,
    mock_vector_repo,
    mock_image_processor,
):
    """
    FastAPI 앱에 가짜 요청을 보낼 클라이언트
    """
    def override_get_db():
        yield db_session
    
    async def override_get_current_user_id():
        return UUID("1cfc6873-82ce-4ecc-b1ec-17abee6507cc")
    
    def override_get_cache_repository():
        return mock_cache_repo
    
    def override_get_vector_repository():
        return mock_vector_repo
    
    def override_get_image_processor():
        return mock_image_processor
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_cache_repository] = override_get_cache_repository
    app.dependency_overrides[get_vector_repository] = override_get_vector_repository
    app.dependency_overrides[get_image_processor] = override_get_image_processor

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    
    app.dependency_overrides.clear()
