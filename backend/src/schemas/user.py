from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str  # plain, will be hashed before save


class UserRead(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    registered_at: datetime

    class Config:
        from_attributes = True
