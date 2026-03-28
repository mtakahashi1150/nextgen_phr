"""マッチングリクエストモデル"""
from sqlalchemy import Column, String, DateTime, TypeDecorator, Boolean, Text, ForeignKey, Enum, JSON, Numeric, Integer
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


class MatchingStatus(str, PyEnum):
    """マッチングステータス"""
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class MatchingRequest(Base):
    """マッチングリクエストテーブル"""
    __tablename__ = "matching_requests"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # マッチング元（患者）と先（企業）
    from_user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    to_company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False)
    
    # ステータス
    status = Column(Enum(MatchingStatus), default=MatchingStatus.SENT, nullable=False)
    
    # マッチング条件
    health_conditions = Column(JSON, nullable=True)  # e.g., ["diabetes", "hypertension"]
    required_studies = Column(JSON, nullable=True)  # e.g., ["blood_test", "heart_monitoring"]
    compensation_type = Column(String(50), nullable=True)  # monetary, gift, free_service
    compensation_amount = Column(Numeric(10, 2), nullable=True)
    
    # リクエスト詳細
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    study_duration_days = Column(Integer, nullable=True)
    
    # 有効期限（30日がデフォルト）
    expires_at = Column(DateTime, nullable=False)
    viewed_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)  # 受記/拒否された日時
    
    response_reason = Column(Text, nullable=True)  # 拒否理由など
    
    # メタデータ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MatchingRequest(id={self.id}, from_user={self.from_user_id}, to_company={self.to_company_id}, status={self.status})>"
