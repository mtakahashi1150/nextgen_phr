"""マッチングスキーマ"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MatchingStatus(str, Enum):
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class CompensationType(str, Enum):
    MONETARY = "monetary"
    SERVICE_CREDIT = "service_credit"
    HEALTH_INSIGHTS = "health_insights"
    NONE = "none"


class MatchingRequestCreate(BaseModel):
    company_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    health_conditions: Optional[Dict[str, Any]] = None
    study_duration_days: Optional[int] = Field(None, gt=0, le=365)
    compensation_type: CompensationType = CompensationType.NONE
    compensation_amount: Optional[float] = Field(None, gt=0)


class MatchingRequestUpdate(BaseModel):
    status: MatchingStatus
    response_reason: Optional[str] = Field(None, max_length=500)


class MatchingRequestResponse(BaseModel):
    id: str
    from_user_id: str
    to_company_id: str
    title: str
    description: str
    status: MatchingStatus
    health_conditions: Optional[Dict[str, Any]]
    study_duration_days: Optional[int]
    compensation_type: CompensationType
    compensation_amount: Optional[float]
    expires_at: datetime
    viewed_at: Optional[datetime]
    responded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MatchingListResponse(BaseModel):
    id: str
    to_company_id: str
    title: str
    status: MatchingStatus
    compensation_type: CompensationType
    compensation_amount: Optional[float]
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
