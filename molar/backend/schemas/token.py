from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenVersionControl(Token):
    user_header: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
