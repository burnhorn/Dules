# from app.infrastructure.db.repositories.user import UserRepository
from app.core.exceptions import KairosException
from app.core.security import get_password_hash
from app.domain.interfaces import UserRepository
from app.domain.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise KairosException(
                message="이미 등록된 이메일입니다.",
                code="EMAIL_DUPLICATED",
                status_code=400,
            )

        hashed_pw = get_password_hash(user_in.password)

        saved_user = await self.repo.create(user_in, hashed_pw)

        # 트랜젝션 확정
        await self.repo.commit()
        await self.repo.refresh(saved_user)

        return UserResponse.model_validate(saved_user)
