from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timezone
from jose import jwt

from app.infrastructure.db.models.user import User
from app.core.config import settings
from app.core.exceptions import CredentialsException
from app.core.security import verify_password, create_access_token
from app.domain.schemas.token import Token
from app.domain.interfaces import TokenRepository

class AuthService:
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> User:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException
    
        return user
    
    def create_token_for_user(self, user: User) -> Token:
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token)
    
    async def logout(self, token: str):
        """
        로그아웃: 토큰을 블랙리스트에 등록
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")

            if not exp:
                return
            
            current_time = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - current_time)

            # 토큰 유효시간이 남아 있음에도 로그아웃했을 시 블랙리스트에 등록
            if ttl > 0:
                await self.token_repo.add_to_blacklist(token, ttl)
        
        except Exception as e:
            print(f"Logout warning: {e}")
