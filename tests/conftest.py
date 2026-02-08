import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.interfaces import (
    ScheduleRepository,
    VectorRepository,
    ImageProcessor,
    CacheRepository
)

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
    return AsyncMock(spec=CacheRepository)