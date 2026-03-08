from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자의 질문")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI의 답변")


class AIImageResponse(BaseModel):
    title: str = Field(description="일정의 핵심 제목 (예: 팀 주간 회의, 결혼식)")
    description: Optional[str] = Field(None, description="일정의 기본 상세 내용")
    type: str = Field(description="EVENT(시간이 정해진 약속) 또는 TASK(할일/마감일)")
    start_at: Optional[str] = Field(None, description="시작 시간 (ISO 8601 형식)")
    end_at: Optional[str] = Field(None, description="종료 시간 (ISO 8601 형식)")
    deadline: Optional[str] = Field(None, description="마감일 (ISO 8601 형식, TASK 일 경우)")

    location: Optional[str] = Field(None, description="일정이 진행되는 장소 (없으면 null)")
    preparations: Optional[str] = Field(None, description="이 일정을 위해 챙겨야 할 준비물 (예: 신분증, 노트북, 축의금 등). 맥락상 필요해 보이면 AI가 추론할 것.")
    comment: Optional[str] = Field(None, description="바쁜 직장인을 위해 AI 비서의 센스 있는 조언 1~2문장 (예: 거리가 머니 일찍 출발하세요, 비가 오니 우산을 챙기세요 등.)")


class AIImageResponseList(BaseModel):
    schedules: List[AIImageResponse] = Field(description="이미지에서 추출된 하나 이상의 일정 목록")


class SearchIntent(BaseModel):
    is_shcedule_query: bool = Field(description="일정을 검색하거나 묻는 질문인지 여부")
    start_date: Optional[datetime] = Field(None, description="검색하려는 기간의 시작일 (예: 오늘, 내일, 다음주 월요일)")
    end_date: Optional[datetime] = Field(None, description="검색하려는 기간의 종료일(예: 이번주 금요일)")
    keyword: Optional[str] = Field(None, description="검색어 (예: '회의', '특정 사람 이름'). 없으면 null")
