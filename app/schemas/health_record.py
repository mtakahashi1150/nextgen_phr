"""ヘルスレコードスキーマ"""
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List
from enum import Enum


class RecordTypeEnum(str, Enum):
    """レコード種別"""
    HEALTH_CHECKUP = "health_checkup"
    IOT_DATA = "iot_data"
    DOCTOR_INPUT = "doctor_input"
    AI_ANALYSIS = "ai_analysis"


class HealthRecordBase(BaseModel):
    """ヘルスレコード基本スキーマ"""
    record_type: RecordTypeEnum
    data: Dict[str, Any]
    medical_condition: Optional[str] = None
    medication: Optional[List[Dict[str, Any]]] = None
    medical_history: Optional[List[Dict[str, Any]]] = None


class HealthRecordCreate(HealthRecordBase):
    """ヘルスレコード作成スキーマ"""
    pass


class HealthRecordUpdate(BaseModel):
    """ヘルスレコード更新スキーマ"""
    record_type: Optional[RecordTypeEnum] = None
    data: Optional[Dict[str, Any]] = None
    medical_condition: Optional[str] = None
    medication: Optional[List[Dict[str, Any]]] = None
    medical_history: Optional[List[Dict[str, Any]]] = None


class HealthRecordResponse(HealthRecordBase):
    """ヘルスレコード応答スキーマ"""
    id: UUID
    user_id: UUID
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HealthRecordListResponse(BaseModel):
    """ヘルスレコードリスト応答"""
    id: UUID
    user_id: UUID
    record_type: RecordTypeEnum
    recorded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
