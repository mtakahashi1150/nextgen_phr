"""マッチングサービステスト"""
import pytest
from datetime import datetime, timedelta
from app.services.matching_service import MatchingService
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.schemas.matching import (
    MatchingRequestCreate, MatchingStatus, CompensationType
)
from app.schemas.company import CompanyCreate
from app.schemas.user import UserCreate


@pytest.fixture
def test_user(db):
    """テストユーザー"""
    user_data = UserCreate(email="user@matching.com", name="Matching User", password="Pass123!")
    return UserService.create_user(db, user_data)


@pytest.fixture
def test_company(db):
    """テスト企業"""
    company_data = CompanyCreate(
        name="Matching Research",
        email="research@matching.com",
        business_registration_number="BR-MATCH",
        password="Pass123!"
    )
    return CompanyService.create_company(db, company_data)


class TestMatchingService:
    """マッチングサービス"""
    
    def test_create_matching_request(self, db, test_user, test_company):
        """マッチングリクエスト作成"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Health Study",
            description="A health monitoring study",
            compensation_type=CompensationType.MONETARY,
            compensation_amount=500.0
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        assert matching.status == MatchingStatus.SENT
        assert matching.from_user_id == test_user.id
        assert matching.compensation_amount == 500.0
    
    def test_mark_as_viewed(self, db, test_user, test_company):
        """マッチングリクエストを閲覧済みに"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="View Test",
            description="Test"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        viewed = MatchingService.mark_as_viewed(db, matching.id)
        assert viewed.status == MatchingStatus.VIEWED
        assert viewed.viewed_at is not None
    
    def test_accept_matching_request(self, db, test_user, test_company):
        """マッチングリクエスト受理"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Accept Test",
            description="Accept this"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        accepted = MatchingService.accept_request(
            db, matching.id, reason="Good fit"
        )
        assert accepted.status == MatchingStatus.ACCEPTED
        assert accepted.response_reason == "Good fit"
    
    def test_reject_matching_request(self, db, test_user, test_company):
        """マッチングリクエスト拒否"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Reject Test",
            description="Reject this"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        rejected = MatchingService.reject_request(
            db, matching.id, reason="Not interested"
        )
        assert rejected.status == MatchingStatus.REJECTED
    
    def test_withdraw_matching_request(self, db, test_user, test_company):
        """マッチングリクエスト撤回"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Withdraw Test",
            description="Withdraw this"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        withdrawn = MatchingService.withdraw_request(db, matching.id)
        assert withdrawn.status == MatchingStatus.WITHDRAWN
    
    def test_list_sent_requests(self, db, test_user, test_company):
        """送信したリクエスト一覧"""
        for i in range(2):
            request_data = MatchingRequestCreate(
                company_id=str(test_company.id),
                title=f"Request {i}",
                description=f"Description {i}"
            )
            MatchingService.create_matching_request(
                db, test_user.id, request_data
            )
        
        requests = MatchingService.list_sent_requests(db, test_user.id)
        assert len(requests) == 2
    
    def test_list_received_requests(self, db, test_user, test_company):
        """受信したリクエスト一覧"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Received",
            description="Received request"
        )
        MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        requests = MatchingService.list_received_requests(
            db, test_company.id
        )
        assert len(requests) == 1
    
    def test_check_expired_requests(self, db, test_user, test_company):
        """有効期限切れリクエスト判定"""
        request_data = MatchingRequestCreate(
            company_id=str(test_company.id),
            title="Expiry Test",
            description="Test expiry"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        # 有効期限を過去に
        matching.expires_at = datetime.utcnow() - timedelta(days=1)
        db.commit()
        
        expired_count = MatchingService.check_expired_requests(db)
        assert expired_count == 1
        
        updated = MatchingService.get_matching_request(db, matching.id)
        assert updated.status == MatchingStatus.EXPIRED
