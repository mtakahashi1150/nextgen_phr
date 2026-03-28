"""同意関連のモデル"""
from sqlalchemy import Column, String, DateTime, TypeDecorator, Boolean, Text, ForeignKey, Enum, Integer
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


class ConsentStatus(str, PyEnum):
    """同意ステータス"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsentType(str, PyEnum):
    """同意タイプ"""
    DATA_SHARING = "data_sharing"
    RESEARCH = "research"
    MARKETING = "marketing"
    THIRD_PARTY = "third_party"
    HEALTH_MONITORING = "health_monitoring"


class Consent(Base):
    """同意テーブル"""
    __tablename__ = "consents"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False)
    
    consent_type = Column(Enum(ConsentType), nullable=False)
    status = Column(Enum(ConsentStatus), default=ConsentStatus.PENDING, nullable=False)
    
    description = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # メタデータ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # リレーション
    audit_logs = relationship("AuditLog", back_populates="consent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Consent(id={self.id}, user_id={self.user_id}, status={self.status})>"


class AuditLog(Base):
    """監査ログテーブル"""
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    consent_id = Column(GUID(), ForeignKey("consents.id"), nullable=False)
    
    action = Column(String(50), nullable=False)  # created, updated, accepted, rejected, withdrawn
    old_status = Column(Enum(ConsentStatus), nullable=True)
    new_status = Column(Enum(ConsentStatus), nullable=True)
    
    user_ip = Column(String(45), nullable=True)  # IPv4/IPv6対応
    user_agent = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # リレーション
    consent = relationship("Consent", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, status={self.new_status})>"
