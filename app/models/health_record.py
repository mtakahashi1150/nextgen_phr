"""ヘルスレコードモデル"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.db.database import Base


class GUID(TypeDecorator):
    """PostgreSQL UUID型とSQLite String型互換のカスタムタイプ"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)


class RecordType(str, PyEnum):
    """レコード種別"""
    HEALTH_CHECKUP = "health_checkup"
    IOT_DATA = "iot_data"
    DOCTOR_INPUT = "doctor_input"
    AI_ANALYSIS = "ai_analysis"


class HealthRecord(Base):
    """ヘルスレコードテーブル"""
    __tablename__ = "health_records"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    
    # レコード種別
    record_type = Column(Enum(RecordType), nullable=False)
    
    # ヘルスデータ（JSON）
    data = Column(JSON, nullable=False, default={})
    
    # 医療情報
    medical_condition = Column(String(255), nullable=True)
    medication = Column(JSON, nullable=True, default=[])
    medical_history = Column(JSON, nullable=True, default=[])
    
    # メタデータ
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, user_id={self.user_id}, type={self.record_type})>"
