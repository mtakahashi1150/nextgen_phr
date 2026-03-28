"""ユーザースキーマ"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    """ユーザー基本スキーマ"""
    email: EmailStr
    name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """ユーザー作成スキーマ"""
    password: str


class UserUpdate(BaseModel):
    """ユーザー更新スキーマ"""
    name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    gdpr_accepted: Optional[bool] = None
    marketing_consent: Optional[bool] = None


class UserResponse(UserBase):
    """ユーザー応答スキーマ"""
    id: UUID
    gdpr_accepted: bool
    marketing_consent: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """ユーザーリスト応答"""
    id: UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
