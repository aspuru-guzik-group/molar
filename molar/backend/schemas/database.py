# std
from typing import List, Optional

# external
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


class DatabaseInformation(BaseModel):
    table_name: str
    column_name: str
    type: str
    subtype: Optional[str]
    is_nullable: str
    constraint_name: Optional[str]
    containt_type: Optional[str]
    references: Optional[str]
