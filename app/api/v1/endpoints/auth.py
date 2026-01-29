from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm # form-data 형식
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_auth_servcie
from app.services.auth_service import AuthService
from app.domain.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_servcie)
):
    
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)

    return auth_service.create_token_for_user(user)