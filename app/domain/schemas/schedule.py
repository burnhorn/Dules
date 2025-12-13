from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

# 일정 타입 정의 (슈퍼타입/서브타입 구분용)
class ScheduleType(str, Enum):
    EVENT = "EVENT" # 시간 확정 일정 (회의, 약속)
    TASK = 'TASK' # 마감 기반 할 일 (보고서 작성, 공부)


# 공통 속성 정의
class ScheduleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="일정 제목")
    description: Optional[str] = Field(None, description="상세 내용")
    type: ScheduleType

    # Event용 필드
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    # Task용 필드
    deadline: Optional[datetime] = None

# 생성 요청 스키마
class ScheduleCreate(ScheduleBase):

    @model_validator(mode='after')
    def check_constraints(self):
        """
        타입에 따른 필수 값 검증 로직
        객체는 생성되는 순간부터 유효함이 보장됨
        """

        # Event
        if self.type == ScheduleType.EVENT:
            if not self.start_at or not self.end_at:
                raise ValueError("이벤트(EVENT)는 시작 시간과 종료 시간이 필수입니다.")
            if self.start_at >= self.end_at:
                raise ValueError("종료 시간은 시작 시간보다 뒤여야 합니다.")
            
        if self.type == ScheduleType.TASK:
            # if not self.deadline:
            #     raise ValueError("할 일(TASK)은 마감일이 필수입니다.")
            pass
            
        return self
    

# 조회 응답 스키마
class ScheduleResponse(ScheduleBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 수정 스키마
class ScheduleUpdate(BaseModel):
    """
    일정 수정 요청 스키마
    - 모든 필드는 Optional로 설정하여 변경할 값만 보냅니다.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="일정 제목")
    description: Optional[str] = Field(None, description="상세 내용")
    type: Optional[ScheduleType] = None

    # Event용 필드
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

    # Task용 필드
    deadline: Optional[datetime] = None