import json
import base64
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage

from app.core.config import settings
from app.domain.interfaces import ImageProcessor
from app.domain.schemas.schedule import ScheduleCreate

class GeminiImageProcessor(ImageProcessor):
    def __init__(self):
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
        )

        print("[Vision] GeminiImageProcessor 초기화 완료")

    async def extract_schedule(self, image_bytes: str, mime_type: str, reference_date: datetime) -> ScheduleCreate:
        print("[Vision] 이미지 분석 시작...")

        image_data = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime_type};base64,{image_data}"
        current_time_str = reference_date.strftime("%Y-%m-%d %H:%M:%S")

        message = HumanMessage(
            content=[
                {"type": "text", "text": """
                이 이미지에서 일정 정보를 추출해줘.
                
                [규칙]
                1. title: 일정의 제목.
                2. description: 장소나 준비물 등 상세 내용.
                3. type: 
                   - 시간이 명확하게(시작/종료) 적혀 있으면 'EVENT'
                   - 날짜만 있거나 마감일만 있거나 시간이 명시되지 않았으면 'TASK'로 설정해. (매우 중요!)
                4. start_at/end_at/deadline: YYYY-MM-DDTHH:MM:SS 형식.
                   - 'EVENT'라면 start_at 필수. end_at 없으면 +1시간.
                   - 'TASK'라면 deadline만 설정.
                   - 상대적 시간(내일, 다음주, 오늘 오후 등)은 
                     현재 시각({current_time_str} - 한국 시간 기준)을 기준으로 절대 시간으로 계산해.
                """},
                {"type": "image_url", "image_url": image_url}
            ]
        )

        structured_llm = self.llm.with_structured_output(ScheduleCreate)

        try:
            result = await structured_llm.ainvoke([message])
            print(f"[Vision] 추출 성공: {result.title}")
            return result

        except Exception as e:
            raise ValueError(f"이미지 분석 중 오류 발생: {e}")