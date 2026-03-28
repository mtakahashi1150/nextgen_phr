"""企業モデル"""
from sqlalchemy import Column, String, DateTime, TypeDecorator, Boolean, Text
import uuid
from datetime import datetime
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


class Company(Base):
    """企業テーブル"""
    __tablename__ = "companies"

    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # 企業認証
    business_registration_number = Column(String(50), unique=True, nullable=False)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # メタデータ
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
