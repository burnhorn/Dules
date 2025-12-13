from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import KairosException

def create_app() -> FastAPI:
    app = FastAPI(
        title="Kairos API",
        description="Context-Aware Scheduler Backend",
        version="0.3.0"
    )
    
    origins = [
        "http://localhost:5173",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 비즈니스 로직 커스텀 예외 처리 
    @app.exception_handler(KairosException)
    async def kairos_exception_handler(request: Request, exc: KairosException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    # FastAPI/Starlette 기본 HTTP 예외 처리(404 Not Found 등)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": f'HTTP_{exc.status_code}',
                "message": str(exc.detail),
            }
        )
    
    # Pydantic 유효성 검사 실패 처리 (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        for error in errors:
            if 'ctx' in error:
                error['ctx'] = {k: str(v) for k, v in error['ctx'].items()}

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "code": "VALIDATION_ERROR",
                "message": "입력 값이 올바르지 않습니다.",
                "details": jsonable_encoder(errors)
            }
        )
    
    # 예상치 못한 서버 에러 처리 (500)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # 운영 환경에서는 Sentry 알림 변경
        print(f"[CRITICAL] Unhandled Exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "INTERNAL_SERVER_ERROR",
                'message': "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            }
        )

    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)