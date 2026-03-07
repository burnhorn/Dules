from datetime import datetime
from uuid import UUID

from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

from app.domain.interfaces import Llm, VectorRepository
from app.domain.interfaces import ScheduleRepository
from app.domain.schemas.chat import ChatRequest, ChatResponse, SearchIntent


class ChatService:
    def __init__(self, vector_repo: VectorRepository, schedule_repo: ScheduleRepository, llm: Llm):
        self.vector_repo = vector_repo
        self.schedule_repo = schedule_repo
        self.llm = llm

        self.intent_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )

    async def chat(self, user_id: UUID, request: ChatRequest) -> ChatResponse:
        """
        Hybrid Retrieval (SQL + Vector 동시에 검색)
        """
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        extractor = self.intent_llm.with_structured_output(SearchIntent)
        intent_prompt = f"""
            현재 시각: {current_time_str} (KST)
            사용자의 질문에서 검색 기간과 키워드를 추출하세요.
            상대적인 시간(내일, 이번 주 등)은 현재 시각을 기준으로 절대 시간으로 변환하세요.
            
            [주의] end_date(종료일)는 반드시 해당 날짜의 23:59:59로 설정하세요. (예: 주말은 일요일 23:59:59)
            
            질문: "{request.message}
        """
        intent: SearchIntent = await extractor.ainvoke([HumanMessage(content=intent_prompt)])

        db_context = ""
        vec_context = ""
        
        # SQL
        if intent.is_shcedule_query:
            exact_schedules = await self.schedule_repo.search_by_date_and_keyword(
                user_id=user_id,
                start_date=intent.start_date,
                end_date=intent.end_date,
                keyword=intent.keyword
            )

        if exact_schedules:
            db_context = "[확정한 일정 데이터]\n" + "\n".join(
                [f" - {s.title} (시작: {s.start_at}, 종료: {s.end_at or '지정안됨'}, 마감: {s.deadline or '지정안됨'})" for s in exact_schedules]
            )

        # Vector
        relevant_docs = await self.vector_repo.search(
            query=request.message, user_id=user_id, limit=3
        )
        if relevant_docs:
            vec_context = "[관련된 과거 기억/맥락]\n" + "\n".join([f"- {doc}" for doc in relevant_docs])

        combined_context = f"{db_context}\n\n{vec_context}".strip()

        if not combined_context:
            combined_context = "관련된 일정이 없습니다."

        answer = await self.llm.ask(question=request.message, context=combined_context)

        return ChatResponse(answer=answer)
