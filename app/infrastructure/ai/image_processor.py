import base64
from datetime import datetime

from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.domain.interfaces import ImageProcessor
from app.domain.schemas.chat import AIImageResponseList
from app.domain.schemas.schedule import ScheduleCreate


class GeminiImageProcessor(ImageProcessor):
    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
        )

        print("[Vision] GeminiImageProcessor 초기화 완료")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def extract_schedule(
        self, image_bytes: bytes, mime_type: str, reference_date: datetime
    ) -> ScheduleCreate:
        print("[Vision] 이미지 분석 시작...")

        image_data = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime_type};base64,{image_data}"
        current_time_str = reference_date.strftime("%Y-%m-%d %H:%M:%S")

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"""
                        당신은 바쁜 금융권 직장인을 돕는 최고의 AI 비서입니다.
                        사용자는 보안망 때문에 PC에서 일정을 옮기지 못해, 모니터 화면(엑셀/달력), 화이트보드, 수첩 메모를 스마트폰으로 대충 찍어서 업로드합니다.
                        이 이미지에서 일정 정보를 추출해 주세요.

                        현재 한국 기준 시각:
                        {current_time_str} (KST)

                        [시간 변환 규칙]
                        - 오늘 → {current_time_str} 날짜
                        - 내일 → +1일
                        - 모레 → +2일
                        - 오전/오후 시간을 정확한 24시간제로 변환
                        - 모든 시간은 ISO8601 datetime 형식으로 반환
                        - timezone은 KST 기준

                        이미지에서 일정 정보를 추출하세요.
                
                    [분석 규칙]
                    1. title: 일정의 핵심 제목.
                    2. type: 
                    - 시간이 명확하게(시작/종료) 적혀 있으면 'EVENT'
                    - 날짜만 있거나 마감일만 있거나 시간이 없으면 'TASK'
                    3. start_at/end_at/deadline: 
                    - 상대적 시간(내일, 오늘 오후 등)은 위 시간 변환 규칙에 따라 계산하세요.
                    
                    [특별 임무]
                    4. location: 장소가 보이면 추출하세요.
                    5. preparations: 일정 성격을 파악해 필요한 준비물을 센스 있게 유추하세요. (예: 미팅 -> 명함/노트북)
                    6. ai_comment: 직장인을 위한 실용적인 조언을 1~2문장으로 작성하세요.
                """,
                },
                {
                    "type": "image_url",
                    "image_url": image_url,
                },
            ]
        )

        structured_llm = self.llm.with_structured_output(AIImageResponseList)
        
        try:
            result = await structured_llm.ainvoke([message])
            print(f"[Vision] 추출 성공: 총 {len(result.schedules)}개의 일정 발견")

            description_parts = []
            final_schedules = []
            
            for item in result.schedules:
                description_parts = []

                if item.description:
                    description_parts.append(item.description)
                if item.location:
                    description_parts.append(f"장소: {item.location}")
                if item.preparations:
                    description_parts.append(f"준비물: {item.preparations}")
                if item.comment:
                    description_parts.append(f"비서 조언: {item.comment}")
            
                final_description = "\n\n".join(description_parts)

                final_schedule = ScheduleCreate(
                    title=item.title,
                    type=item.type,
                    start_at=item.start_at,
                    end_at=item.end_at,
                    deadline=item.deadline,
                    description=final_description
                )
                final_schedules.append(final_schedule)

            return final_schedules

        except Exception as e:
            raise ValueError(f"이미지 분석 중 오류 발생: {e}")
