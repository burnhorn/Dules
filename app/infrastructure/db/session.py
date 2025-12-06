from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


# 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# 세션 생성
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False # Lazy Load 방지
)