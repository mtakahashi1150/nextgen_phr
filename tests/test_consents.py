"""同意エンドポイントテスト"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.services.consent_service import ConsentService
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.schemas.consent import ConsentCreate, ConsentStatus, ConsentType
from app.schemas.company import CompanyCreate
from app.schemas.user import UserCreate


    """テスト用 HTTP クライアント"""
    with Client(app=app, base_url="http://testserver") as c:
        yield c




class TestConsentCreation:
    """同意作成テスト"""
    
    def test_create_consent_success(self, db, test_user, test_company):
        """正常な同意作成"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.RESEARCH,
            description="I consent to participate in this research study"
        )
        
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data,
            user_ip="192.168.1.1", user_agent="TestAgent/1.0"
        )
        
        assert consent.id is not None
        assert consent.user_id == test_user.id
        assert consent.company_id == test_company.id
        assert consent.status == ConsentStatus.PENDING
        assert consent.consent_type == ConsentType.RESEARCH
    
    def test_create_consent_with_expiry(self, db, test_user, test_company):
        """有効期限付き同意作成"""
        expires_at = datetime.utcnow() + timedelta(days=30)
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.DATA_SHARING,
            description="Data sharing consent",
            expires_at=expires_at
        )
        
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        assert consent.expires_at is not None


class TestConsentRetrieval:
    """同意取得テスト"""
    
    def test_list_user_consents(self, db, test_user, test_company):
        """ユーザーの同意一覧取得"""
        # 複数の同意を作成
        for i, consent_type in enumerate([ConsentType.RESEARCH, ConsentType.DATA_SHARING]):
            consent_data = ConsentCreate(
                company_id=test_company.id,
                consent_type=consent_type,
                description=f"Consent {i+1}"
            )
            ConsentService.create_consent(
                db, test_user.id, test_company.id, consent_data
            )
        
        consents = ConsentService.list_user_consents(db, test_user.id)
        assert len(consents) == 2
    
    def test_list_company_consents(self, db, test_user, test_company):
        """企業が受信した同意一覧"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.RESEARCH,
            description="Research consent"
        )
        ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        consents = ConsentService.list_company_consents(
            db, test_company.id
        )
        assert len(consents) == 1
        assert consents[0].user_id == test_user.id
    
    def test_get_consent(self, db, test_user, test_company):
        """同意情報取得"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.HEALTH_MONITORING,
            description="Health monitoring"
        )
        created_consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        retrieved = ConsentService.get_consent(db, created_consent.id)
        assert retrieved.id == created_consent.id
        assert retrieved.consent_type == ConsentType.HEALTH_MONITORING


class TestConsentStatusUpdate:
    """同意ステータス更新テスト"""
    
    def test_accept_consent(self, db, test_user, test_company):
        """同意を受理"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.RESEARCH,
            description="Research consent"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        updated = ConsentService.update_consent_status(
            db, consent.id, ConsentStatus.ACCEPTED,
            user_ip="192.168.1.1"
        )
        
        assert updated.status == ConsentStatus.ACCEPTED
        assert updated.updated_at is not None
    
    def test_reject_consent(self, db, test_user, test_company):
        """同意を拒否"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.MARKETING,
            description="Marketing consent"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        updated = ConsentService.update_consent_status(
            db, consent.id, ConsentStatus.REJECTED
        )
        
        assert updated.status == ConsentStatus.REJECTED
    
    def test_withdraw_consent(self, db, test_user, test_company):
        """同意を撤回"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.DATA_SHARING,
            description="Data sharing"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        # まず受理
        ConsentService.update_consent_status(
            db, consent.id, ConsentStatus.ACCEPTED
        )
        
        # その後撤回
        withdrawn = ConsentService.withdraw_consent(
            db, consent.id, user_ip="192.168.1.1"
        )
        
        assert withdrawn.status == ConsentStatus.WITHDRAWN


class TestAuditLogging:
    """監査ログテスト"""
    
    def test_audit_log_creation(self, db, test_user, test_company):
        """監査ログが作成されることを確認"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.RESEARCH,
            description="Research consent"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data,
            user_ip="192.168.1.1", user_agent="Chrome/91.0"
        )
        
        logs = ConsentService.get_audit_logs(db, consent.id)
        assert len(logs) > 0
        assert logs[0].action == "created"
        assert logs[0].new_status == ConsentStatus.PENDING
    
    def test_audit_log_status_change(self, db, test_user, test_company):
        """ステータス変更が監査ログに記録されることを確認"""
        consent_data = ConsentCreate(
            company_id=test_company.id,
            consent_type=ConsentType.RESEARCH,
            description="Research"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        ConsentService.update_consent_status(
            db, consent.id, ConsentStatus.ACCEPTED,
            user_ip="192.168.1.1"
        )
        
        logs = ConsentService.get_audit_logs(db, consent.id)
        assert len(logs) >= 2
        assert logs[0].old_status == ConsentStatus.PENDING
        assert logs[0].new_status == ConsentStatus.ACCEPTED
