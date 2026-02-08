from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # OAuth2 표준 타입


class TokenData(BaseModel):
    user_id: str | None = None
