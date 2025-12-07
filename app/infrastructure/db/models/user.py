import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base

class User(Base):
    """
    사용자(User) 엔티티
    - 핵심: 비밀번호는 반드시 Hash 된 상태로 저장된다.
    """
    __tablename__ = "users"

    # 식별자
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 기본 정보
    email = Column(String(255), unique=True, nullable=False, index=True) # 검색을 위한 index 추가
    name = Column(String(100), nullable=False)

    # 객체 일관성: 명확한 이름 사용(평문 저장 금지 암시)
    hashed_password = Column(String(255), nullable=False)

    # 상태 관리
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 메타 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 정리
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")