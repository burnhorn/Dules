from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.models.user import User
from app.core.exceptions import CredentialsException
from app.core.security import verify_password, create_access_token
from app.domain.schemas.token import Token

class AuthService:
    # Repository 없이 Service Layer에서 DB 조회
    # 복잡해지면 UserRepository 분리

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> User:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException
    
        return user
    
    def create_token_for_user(self, user: User) -> Token:
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token)