from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)


# 회원가입 요청 (비밀번호 입력 받기)
class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, description="비밀번호는 최소 8자 이상입니다."
    )


# DB 저장용 내부 스키마 (해시된 비밀번호 사용)
class UserInDB(UserBase):
    hashed_password: str


# 클라이언트 응답용 (비밀번호 미포함)
class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
