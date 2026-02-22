from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.interfaces import UserRepository
from app.domain.schemas.user import UserCreate
from app.infrastructure.db.models.user import User


class SQLAlchemyUserRepository(UserRepository):
    """
    User 테이블을 위한 구현체
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        ID(UUID)로 유저 조회 (Refresh Token 검증 및 최신 권한 확인용)
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str, load_schedules: bool = False) -> Optional[User]:
        """
        이메일로 유저 조회 (중복 검사용)
        """
        query = select(User).where(User.email == email)
        if load_schedules:
            query = query.options(selectinload(User.schedules))

        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, user_create: UserCreate, hashed_password) -> User:
        """
        ORM 객체 생성
        """
        db_user = User(
            email=user_create.email,
            name=user_create.name,
            hashed_password=hashed_password,
        )

        self.db.add(db_user)
        return db_user

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance):
        await self.db.refresh(instance)
