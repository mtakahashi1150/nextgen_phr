"""企業スキーマ"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    business_registration_number: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class CompanyCreate(CompanyBase):
    password: str = Field(..., min_length=8)


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class CompanyResponse(CompanyBase):
    id: str
    verified: bool
    verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    id: str
    name: str
    email: str
    industry: Optional[str]
    verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
