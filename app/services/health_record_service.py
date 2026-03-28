"""ヘルスレコード管理サービス"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.health_record import HealthRecord
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate


class HealthRecordService:
    """ヘルスレコード管理サービス"""
    
    @staticmethod
    def create_health_record(db: Session, user_id: UUID, record_create: HealthRecordCreate) -> HealthRecord:
        """ヘルスレコードを作成"""
        db_record = HealthRecord(
            user_id=user_id,
            record_type=record_create.record_type,
            data=record_create.data,
            medical_condition=record_create.medical_condition,
            medication=record_create.medication,
            medical_history=record_create.medical_history
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record
    
    @staticmethod
    def get_health_record_by_id(db: Session, record_id: UUID) -> Optional[HealthRecord]:
        """IDでヘルスレコードを取得"""
        return db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    
    @staticmethod
    def get_user_health_records(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[HealthRecord]:
        """ユーザーのヘルスレコード一覧を取得"""
        return db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id
        ).order_by(HealthRecord.recorded_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_health_records_by_type(
        db: Session,
        user_id: UUID,
        record_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[HealthRecord]:
        """ユーザーのレコード種別でフィルタリング"""
        return db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id,
            HealthRecord.record_type == record_type
        ).order_by(HealthRecord.recorded_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_health_record(db: Session, record_id: UUID, record_update: HealthRecordUpdate) -> Optional[HealthRecord]:
        """ヘルスレコードを更新"""
        db_record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not db_record:
            return None
        
        update_data = record_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_record, field, value)
        
        db.commit()
        db.refresh(db_record)
        
        return db_record
    
    @staticmethod
    def delete_health_record(db: Session, record_id: UUID) -> bool:
        """ヘルスレコードを削除"""
        db_record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not db_record:
            return False
        
        db.delete(db_record)
        db.commit()
        
        return True
    
    @staticmethod
    def get_latest_health_record(db: Session, user_id: UUID) -> Optional[HealthRecord]:
        """ユーザーの最新ヘルスレコードを取得"""
        return db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id
        ).order_by(HealthRecord.recorded_at.desc()).first()
