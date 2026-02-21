import asyncio
import uuid
import structlog
from typing import List
from uuid import UUID

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.domain.interfaces import VectorRepository

logger = structlog.get_logger()

class PGVectorRepository(VectorRepository):
    def __init__(self):
        self.CURRENT_MODEL = settings.GOOGLE_EMBEDDINGS_MODEL
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.CURRENT_MODEL, google_api_key=settings.GOOGLE_API_KEY
        )

        # [이슈] 동기용 드라이버 사용 (psycopg)
        # SQLAlchemy URL의 asyncpg => psycopg 교체
        self.connection_string = settings.DATABASE_URL.replace(
            "postgresql+asyncpg", "postgresql+psycopg"
        )

        sanitized_model_name = self.CURRENT_MODEL.replace("/", "_").replace("-", "_")
        self.collection_name = f"dules_schedules_{sanitized_model_name}"

        # PGVector를 동기 모드로 초기화
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_string,
            use_jsonb=True,
            create_extension=False,
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def save(self, text: str, user_id: UUID, metadata: dict = None) -> None:
        logger.info("vector_save_start", text_snippet=text[:10], collection=self.collection_name)

        if metadata is None:
            metadata = {}
        metadata["user_id"] = str(user_id)
        metadata["model_version"] = self.CURRENT_MODEL

        doc = Document(page_content=text, metadata=metadata)
        doc_id = metadata.get("schedule_id", str(uuid.uuid4()))

        # 동기 메서드(add_documents)를 스레드 풀에서 실행
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.vector_store.add_documents(documents=[doc], ids=[doc_id]),
            )
            logger.info("vector_save_suceess", doc_id=doc_id)
        except Exception as e:
            logger.error("vector_save_failed", error=str(e))

    async def search(self, query: str, user_id: UUID, limit: int = 3) -> List[str]:
        logger.info("[PGVector] 검색 요청", {query})

        loop = asyncio.get_running_loop()

        # 검색 또한 스레드 풀
        results = await loop.run_in_executor(
            None,
            lambda: self.vector_store.similarity_search(
                query, k=limit, filter={"user_id": str(user_id)}
            ),
        )
        logger.info("[PGVector] 검색 완료", {len(results)})
        return [doc.page_content for doc in results]

    async def delete(self, doc_id: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: self.vector_store.delete(ids=[doc_id]))
