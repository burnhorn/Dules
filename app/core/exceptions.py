from typing import Any, Dict, Optional


class DulesException(Exception):
    """
    시스템 전반에서 발생하는 비즈니스 로직 예외의 부모 클래스
    """

    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class CredentialsException(DulesException):
    def __init__(self):
        super().__init__(
            message="자격 증명이 유효하지 않습니다.", code="AUTH_001", status_code=401
        )


class ResourceNotFoundException(DulesException):
    def __init__(self, resource: str):
        super().__init__(
            message=f"요청하신 {resource}를 찾을 수 없습니다.",
            code="NOT_FOUND",
            status_code=404,
        )


class AIProcessingException(DulesException):
    def __init__(self, details: str = None):
        super().__init__(
            message=f"AI 처리 중 오류가 발생했습니다. {details}",
            code="AI_ERROR",
            status_code=503,
        )
