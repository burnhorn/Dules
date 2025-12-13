import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.domain.interfaces import AIBrain
from app.core.config import settings

class FakeBrain(AIBrain):
    """
    개발 및 테스트용 가짜 두뇌
    외부 API를 호출하지 않고 고정된 응답을 반환합니다.
    """
    async def ask(self, question: str, context: str) -> str:
        await asyncio.sleep(0.5)

        return (
            f"[Fake AI 답변]\n"
            f"질문하신 '{question}'에 대해 답변드립니다.\n"
            f"참고한 과거 일정 정보:\n{context or '없음'}"
        )

class GeminiBrain(AIBrain):
    def __init__(self):
        """
        실제 Gemini API 호출용
        """
        print("[Brain] GeminiBrain 초기화 중...")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3
        )

        self.prompt = ChatPromptTemplate.from_template(
            """
            너는 사용자의 일정을 관리해주는 유능한 비서 Kairos야
            아래 제공된 [과거 일정 목록]을 바탕으로 사용자의 [질문]에 친절하게 답변해 줘.
            
            만약 제공된 일정 정보에서 답을 찾을 없다면 솔직하게 정보가 없다고 말해줘.
            없는 내용을 지어내지 마 (Hallucination 방지)

            [과거 일정 목록]
            {context}

            [질문]
            {question}
            """
            )

        self.chain = self.prompt | self.llm | StrOutputParser()
        print("[Brain] GeminiBrain 준비 완료!")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    async def ask(self, question: str, context: str) -> str:
        try:
            response = await self.chain.ainvoke({
                "question": question,
                "context": context
            })
            if response is None:
                    print("[Brain] 답변이 None입니다.")
                    return "죄송합니다. 답변을 생성하는 데 문제가 발생했습니다."
                    
            print(f"[Brain] 답변 완료: {response[:20]}...")
            return response

        except Exception as e:
            print(f"[Brain] 에러 발생: {e}")
            return "죄송합니다. 에러가 발생하여 답변할 수 없습니다."