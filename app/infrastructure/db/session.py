from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    # 비동기 환경에서 커밋 후 속성 접근 시 발생하는 MissingGreenlet 에러 방지 (객체 만료 방지)
    expire_on_commit=False,
)
