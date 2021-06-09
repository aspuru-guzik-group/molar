# std
from datetime import datetime
from typing import Optional

# external
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    is_superuser: bool = False
    is_active: bool = False
    full_name: Optional[str] = None
    created_on: Optional[datetime] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    user_id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
