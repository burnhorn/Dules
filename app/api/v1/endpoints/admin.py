from fastapi import APIRouter, Depends

from app.api.dependencies import allowed_roles_only

router = APIRouter()


@router.get("/status", dependencies=[Depends(allowed_roles_only)])
async def get_system_stats():
    return {
        "user_count": 100,
        "server_status": "healthy",
        "message": "환영합니다. 관리자님.",
    }

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0