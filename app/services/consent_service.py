"""同意サービス"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.consent import Consent, AuditLog, ConsentStatus, ConsentType
from app.schemas.consent import ConsentCreate, ConsentUpdate
import uuid
from datetime import datetime, timedelta


class ConsentService:
    """同意管理サービス"""
    
    @staticmethod
    def create_consent(
        db: Session,
        user_id: str,
        company_id: str,
        consent_data: ConsentCreate,
        user_ip: str = None,
        user_agent: str = None
    ) -> Consent:
        """同意を作成"""
        expires_at = consent_data.expires_at or (datetime.utcnow() + timedelta(days=365))
        
        consent = Consent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            company_id=company_id,
            consent_type=consent_data.consent_type,
            status=ConsentStatus.PENDING,
            description=consent_data.description,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        db.add(consent)
        db.flush()
        
        # 監査ログ作成
        ConsentService._log_action(
            db, consent.id, "created", None,
            ConsentStatus.PENDING, user_ip, user_agent
        )
        
        db.commit()
        db.refresh(consent)
        return consent
    
    @staticmethod
    def get_consent(db: Session, consent_id: str) -> Consent:
        """同意を取得"""
        query = select(Consent).where(Consent.id == consent_id)
        return db.execute(query).scalar_one_or_none()
    
    @staticmethod
    def list_user_consents(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Consent]:
        """ユーザーの同意一覧を取得"""
        query = (
            select(Consent)
            .where(Consent.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).scalars().all()
    
    @staticmethod
    def list_company_consents(
        db: Session,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Consent]:
        """企業が受け取った同意一覧を取得"""
        query = (
            select(Consent)
            .where(Consent.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).scalars().all()
    
    @staticmethod
    def update_consent_status(
        db: Session,
        consent_id: str,
        new_status: ConsentStatus,
        user_ip: str = None,
        user_agent: str = None
    ) -> Consent:
        """同意ステータスを更新"""
        consent = ConsentService.get_consent(db, consent_id)
        if not consent:
            return None
        
        old_status = consent.status
        consent.status = new_status
        consent.updated_at = datetime.utcnow()
        
        # 監査ログ作成
        ConsentService._log_action(
            db, consent_id, "updated", old_status,
            new_status, user_ip, user_agent
        )
        
        db.commit()
        db.refresh(consent)
        return consent
    
    @staticmethod
    def withdraw_consent(
        db: Session,
        consent_id: str,
        user_ip: str = None,
        user_agent: str = None
    ) -> Consent:
        """同意を撤回"""
        return ConsentService.update_consent_status(
            db, consent_id, ConsentStatus.WITHDRAWN, user_ip, user_agent
        )
    
    @staticmethod
    def _log_action(
        db: Session,
        consent_id: str,
        action: str,
        old_status: ConsentStatus = None,
        new_status: ConsentStatus = None,
        user_ip: str = None,
        user_agent: str = None,
        notes: str = None
    ) -> AuditLog:
        """監査ログを作成"""
        log = AuditLog(
            id=str(uuid.uuid4()),
            consent_id=consent_id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            user_ip=user_ip,
            user_agent=user_agent,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(log)
        return log
    
    @staticmethod
    def get_audit_logs(db: Session, consent_id: str) -> list[AuditLog]:
        """監査ログを取得"""
        query = (
            select(AuditLog)
            .where(AuditLog.consent_id == consent_id)
            .order_by(AuditLog.created_at.desc())
        )
        return db.execute(query).scalars().all()
