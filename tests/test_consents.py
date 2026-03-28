"""同意サービステスト"""
import pytest
from datetime import datetime, timedelta
from app.services.consent_service import ConsentService
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.schemas.consent import ConsentCreate, ConsentStatus, ConsentType
from app.schemas.company import CompanyCreate
from app.schemas.user import UserCreate


@pytest.fixture
def test_user(db):
    """テストユーザー"""
    user_data = UserCreate(email="user@test.com", name="Test User", password="Pass123!")
    return UserService.create_user(db, user_data)


@pytest.fixture
def test_company(db):
    """テスト企業"""
    company_data = CompanyCreate(
        name="Test Research",
        email="research@test.com",
        business_registration_number="BR-CONSENT",
        password="Pass123!"
    )
    return CompanyService.create_company(db, company_data)


class TestConsentService:
    """同意サービス"""
    
    def test_create_consent(self, db, test_user, test_company):
        """同意作成"""
        consent_data = ConsentCreate(
            company_id=str(test_company.id),
            consent_type=ConsentType.RESEARCH,
            description="Consent for research"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data,
            user_ip="127.0.0.1"
        )
        
        assert consent.user_id == test_user.id
        assert consent.status == ConsentStatus.PENDING
    
    def test_update_consent_status(self, db, test_user, test_company):
        """同意ステータス更新"""
        consent_data = ConsentCreate(
            company_id=str(test_company.id),
            consent_type=ConsentType.DATA_SHARING,
            description="Data sharing"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        updated = ConsentService.update_consent_status(
            db, consent.id, ConsentStatus.ACCEPTED
        )
        assert updated.status == ConsentStatus.ACCEPTED
    
    def test_withdraw_consent(self, db, test_user, test_company):
        """同意撤回"""
        consent_data = ConsentCreate(
            company_id=str(test_company.id),
            consent_type=ConsentType.RESEARCH,
            description="Consent"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        withdrawn = ConsentService.withdraw_consent(db, consent.id)
        assert withdrawn.status == ConsentStatus.WITHDRAWN
    
    def test_list_user_consents(self, db, test_user, test_company):
        """ユーザーの同意一覧"""
        for i in range(2):
            consent_data = ConsentCreate(
                company_id=str(test_company.id),
                consent_type=ConsentType.RESEARCH,
                description=f"Consent {i}"
            )
            ConsentService.create_consent(
                db, test_user.id, test_company.id, consent_data
            )
        
        consents = ConsentService.list_user_consents(db, test_user.id)
        assert len(consents) == 2
    
    def test_get_audit_logs(self, db, test_user, test_company):
        """監査ログ取得"""
        consent_data = ConsentCreate(
            company_id=str(test_company.id),
            consent_type=ConsentType.RESEARCH,
            description="With audit"
        )
        consent = ConsentService.create_consent(
            db, test_user.id, test_company.id, consent_data
        )
        
        logs = ConsentService.get_audit_logs(db, consent.id)
        assert len(logs) > 0
        assert logs[0].action == "created"
