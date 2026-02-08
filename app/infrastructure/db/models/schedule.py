import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.schemas.schedule import ScheduleType
from app.infrastructure.db.base import Base  # declarative_base()


class Schedule(Base):
    __tablename__ = "schedules"

    # 식별자 전략: UUID 사용 (보안성, 분산환경 고려)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 외래키 (User 테이블과 연결)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 기본 정보
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(SQLEnum(ScheduleType), nullable=False)  # 통합 테이블 전략

    # 시간 정보 (Nullable로 두고 App Layer에서 제어)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    # 메타 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 정의 (User, History...)
    user = relationship("User", back_populates="schedules")
    histories = relationship(
        "ScheduleHistory", back_populates="schedule", cascade="all, delete-orphan"
    )


class ScheduleHistory(Base):
    """
    일정 변경 이력을 저장하는 테이블 (AI 학습 데이터용 Context 제공)
    """

    __tablename__ = "schedule_histories"
    # 식별자 전략: UUID 사용 (보안성, 분산환경 고려)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 외래키 (schedules 테이블과 연결)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False)

    # 이력 관리 (Snapshot 방식)
    previous_title = Column(String(100), nullable=True)
    previous_start_at = Column(DateTime(timezone=True), nullable=True)
    previous_end_at = Column(DateTime(timezone=True), nullable=True)

    # 메타 데이터
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 정의
    schedule = relationship("Schedule", back_populates="histories")
