from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces import UserRepository
from app.domain.schemas.user import UserCreate
from app.infrastructure.db.models.user import User


class SQLAlchemyUserRepository(UserRepository):
    """
    User 테이블을 위한 구현체
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 유저 조회 (중복 검사용)
        """
        query = select(User).where(User.email == email)
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
