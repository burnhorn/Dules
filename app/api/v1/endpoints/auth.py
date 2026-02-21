from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_auth_servcie,
    get_user_service,
    oauth2_schema,
)
from app.domain.schemas.token import Token
from app.domain.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_servcie),
):

    user = await auth_service.authenticate_user(
        form_data.username, form_data.password
    )

    return await auth_service.create_tokens_for_user(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    auth_service: AuthService = Depends(get_auth_servcie),
):
    """
    Refresh Token을 이용하여 새로운 Access Token을 발급
    """
    return await auth_service.refresh_access_token(refresh_token)


@router.post("/signup", response_model=UserResponse, summary="회원가입")
async def register_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    """
    새로운 사용자 등록(user_in: email, password, name)
    """
    return await service.create_user(user_in)


@router.post("/logout", summary="로그아웃")
async def logout(
    access_token: str = Depends(oauth2_schema),
    refresh_token: str = Body(None, embed=True),
    auth_service: AuthService = Depends(get_auth_servcie),
):
    """
    현재 사용 중인 엑세스 토큰을 만료
    """
    await auth_service.logout(access_token, refresh_token)
    return {"message": "로그아웃 되었습니다."}
