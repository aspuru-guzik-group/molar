from typing import List

from pydantic import BaseModel, EmailStr


class DatabaseBase(BaseModel):
    database_name: str
    superuser_fullname: str
    superuser_email: EmailStr
    alembic_revisions: List[str]


class DatabaseCreate(DatabaseBase):
    superuser_password: str


class DatabaseUpdate(DatabaseCreate):
    is_approved: bool
