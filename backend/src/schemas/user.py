from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool


class UserCreate(UserBase):
    password: str  # plain, will be hashed before save
    is_active: bool = True
    is_verified: bool = False


class UserRead(UserBase):
    id: UUID
    registered_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    id: UUID
    email: EmailStr
    username: str
    role_id: UUID
    is_active: bool
    is_verified: bool
