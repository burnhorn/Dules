from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timezone
from jose import JWTError, jwt

from uuid import UUID
from datetime import timedelta

from app.infrastructure.db.models.user import User
from app.core.config import settings
from app.core.exceptions import CredentialsException
from app.core.security import verify_password, create_access_token, create_refresh_token
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
    
    async def create_tokens_for_user(self, user: User) -> Token:
        access_token = create_access_token(subject=user.id,
                                           role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        # Redis에 만료시간(초) 저장
        refresh_ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await self.token_repo.save_refresh_token(
            refresh_token,
            user.id,
            refresh_ttl
        )

        return Token(access_token=access_token, refresh_token=refresh_token)
    
    async def refresh_access_token(self, refresh_token:str) -> Token:
        user_id_str = await self.token_repo.get_refresh_token_user_id(refresh_token)

        if not user_id_str:
            raise CredentialsException()
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise CredentialsException()
        except JWTError:
            raise CredentialsException()
        
        # Refresh Token은 그대로, Access Token만 새로 발급
        new_access_token = create_access_token(subject=user_id_str)

        return Token(access_token=new_access_token, refresh_token=refresh_token)

    async def logout(self, access_token: str, refresh_token: str = None):
        """
        로그아웃: 토큰을 블랙리스트에 등록 및 Refresh Token제거
        """
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")

            if not exp:
                return
            
            current_time = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - current_time)

            # 토큰 유효시간이 남아 있음에도 로그아웃했을 시 블랙리스트에 등록
            if ttl > 0:
                await self.token_repo.add_to_blacklist(access_token, ttl)
        
        except Exception as e:
            print(f"Logout warning: {e}")
        
        if refresh_token:
            await self.token_repo.delete_refresh_token(refresh_token)
