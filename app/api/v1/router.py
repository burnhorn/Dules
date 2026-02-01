from fastapi import APIRouter
from app.api.v1.endpoints import admin, schedules, chat, auth

api_router = APIRouter()

# /schedules 경로로 들어오는 모든 요청을 schedules.router가 처리
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])