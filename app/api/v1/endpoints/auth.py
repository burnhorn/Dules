from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_auth_servcie, get_user_service, oauth2_schema

from app.domain.schemas.token import Token
from app.domain.schemas.user import UserCreate, UserResponse

from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_servcie)
):
    
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)

    return auth_service.create_token_for_user(user)

@router.post("/signup", response_model=UserResponse, summary="회원가입")
async def register_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    새로운 사용자 등록(user_in: email, password, name)
    """
    return await service.create_user(user_in)

@router.post("/logout", summary="로그아웃")
async def logout(
    token: str = Depends(oauth2_schema),
    auth_service: AuthService = Depends(get_auth_servcie)
):
    """
    현재 사용 중인 엑세스 토큰을 만료 시킵니다.
    """
    await auth_service.logout(token)
    return {"message": "로그아웃 되었습니다."}