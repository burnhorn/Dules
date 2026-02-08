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
