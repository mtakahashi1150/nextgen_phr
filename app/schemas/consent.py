"""同意スキーマ"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ConsentType(str, Enum):
    DATA_SHARING = "data_sharing"
    RESEARCH = "research"
    MARKETING = "marketing"
    THIRD_PARTY = "third_party"
    HEALTH_MONITORING = "health_monitoring"


class ConsentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsentCreate(BaseModel):
    company_id: str
    consent_type: ConsentType
    description: str = Field(..., min_length=1, max_length=2000)
    expires_at: Optional[datetime] = None


class ConsentUpdate(BaseModel):
    status: ConsentStatus
    notes: Optional[str] = Field(None, max_length=500)


class ConsentResponse(BaseModel):
    id: str
    user_id: str
    company_id: str
    consent_type: ConsentType
    description: str
    status: ConsentStatus
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: str
    consent_id: str
    action: str
    user_ip: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
