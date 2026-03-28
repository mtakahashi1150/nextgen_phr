"""マッチングリクエストテスト"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.services.matching_service import MatchingService
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.schemas.matching import (
    MatchingRequestCreate, MatchingStatus, CompensationType
)
from app.schemas.company import CompanyCreate
from app.schemas.user import UserCreate




    """テスト用 HTTP クライアント"""
    with Client(app=app, base_url="http://testserver") as c:
        yield c




class TestMatchingRequestCreation:
    """マッチングリクエスト作成テスト"""
    
    def test_create_matching_request(self, db, test_user, test_company):
        """正常なマッチングリクエスト作成"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Diabetes Study Participation",
            description="We are looking for participants with Type 2 diabetes",
            health_conditions={"primary": ["diabetes"], "severity": "mild"},
            study_duration_days=90,
            compensation_type=CompensationType.MONETARY,
            compensation_amount=500.00
        )
        
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        assert matching.id is not None
        assert matching.from_user_id == test_user.id
        assert matching.to_company_id == test_company.id
        assert matching.status == MatchingStatus.SENT
        assert matching.title == "Diabetes Study Participation"
        assert matching.compensation_amount == 500.00
    
    def test_matching_request_default_expiry(self, db, test_user, test_company):
        """デフォルト有効期限（30日）の確認"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Health Study",
            description="A health monitoring study"
        )
        
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        expected_expiry = datetime.utcnow() + timedelta(days=30)
        delta = abs((matching.expires_at - expected_expiry).total_seconds())
        assert delta < 5  # 5秒以内の誤差は許容


class TestMatchingRequestRetrieval:
    """マッチングリクエスト取得テスト"""
    
    def test_get_matching_request(self, db, test_user, test_company):
        """マッチングリクエスト取得"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Blood Test Study",
            description="Blood sampling study"
        )
        created = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        retrieved = MatchingService.get_matching_request(
            db, created.id
        )
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Blood Test Study"
    
    def test_list_sent_requests(self, db, test_user, test_company):
        """送信したマッチングリクエスト一覧"""
        # 複数のリクエストを作成
        for i in range(3):
            request_data = MatchingRequestCreate(
                company_id=test_company.id,
                title=f"Study {i+1}",
                description=f"Study description {i+1}"
            )
            MatchingService.create_matching_request(
                db, test_user.id, request_data
            )
        
        requests = MatchingService.list_sent_requests(db, test_user.id)
        assert len(requests) == 3
    
    def test_list_received_requests(self, db, test_user, test_company):
        """企業が受信したマッチングリクエスト一覧"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Received Study",
            description="Company receives this"
        )
        MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        requests = MatchingService.list_received_requests(
            db, test_company.id
        )
        assert len(requests) == 1
        assert requests[0].to_company_id == test_company.id


class TestMatchingStatusUpdate:
    """マッチングステータス更新テスト"""
    
    def test_mark_as_viewed(self, db, test_user, test_company):
        """メッセージを「閲覧済み」にマーク"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="View Test",
            description="Test viewing"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        assert matching.status == MatchingStatus.SENT
        assert matching.viewed_at is None
        
        viewed = MatchingService.mark_as_viewed(db, matching.id)
        
        assert viewed.status == MatchingStatus.VIEWED
        assert viewed.viewed_at is not None
    
    def test_accept_matching_request(self, db, test_user, test_company):
        """マッチングリクエストを受理"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Accept Test",
            description="Accept this request"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        accepted = MatchingService.accept_request(
            db, matching.id, reason="Great fit for our study"
        )
        
        assert accepted.status == MatchingStatus.ACCEPTED
        assert accepted.responded_at is not None
        assert accepted.response_reason == "Great fit for our study"
    
    def test_reject_matching_request(self, db, test_user, test_company):
        """マッチングリクエストを拒否"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Reject Test",
            description="Reject this"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        rejected = MatchingService.reject_request(
            db, matching.id, reason="Not matching our criteria"
        )
        
        assert rejected.status == MatchingStatus.REJECTED
        assert rejected.responded_at is not None
    
    def test_withdraw_request(self, db, test_user, test_company):
        """マッチングリクエストを撤回"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Withdraw Test",
            description="Withdraw this"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        withdrawn = MatchingService.withdraw_request(db, matching.id)
        
        assert withdrawn.status == MatchingStatus.WITHDRAWN
    
    def test_cannot_withdraw_accepted(self, db, test_user, test_company):
        """受理されたリクエストは撤回できない"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Accepted",
            description="Already accepted"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        # 受理
        MatchingService.accept_request(db, matching.id)
        
        # 撤回を試みる（効果なし）
        result = MatchingService.withdraw_request(db, matching.id)
        
        # ステータスは ACCEPTED のままか確認
        assert result.status == MatchingStatus.ACCEPTED


class TestMatchingExpiration:
    """マッチング有効期限テスト"""
    
    def test_check_expired_requests(self, db, test_user, test_company):
        """有効期限切れのリクエストをマーク"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Expiry Test",
            description="This will expire"
        )
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        # 有効期限を過去に変更
        matching.expires_at = datetime.utcnow() - timedelta(days=1)
        db.commit()
        
        expired_count = MatchingService.check_expired_requests(db)
        
        assert expired_count == 1
        
        # ステータスが EXPIRED になっていることを確認
        updated = MatchingService.get_matching_request(db, matching.id)
        assert updated.status == MatchingStatus.EXPIRED


class TestMatchingCompensation:
    """補償管理テスト"""
    
    def test_monetary_compensation(self, db, test_user, test_company):
        """現金補償の設定"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Paid Study",
            description="Monetary compensation",
            compensation_type=CompensationType.MONETARY,
            compensation_amount=1000.00
        )
        
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        assert matching.compensation_type == CompensationType.MONETARY
        assert matching.compensation_amount == 1000.00
    
    def test_no_compensation(self, db, test_user, test_company):
        """補償なし"""
        request_data = MatchingRequestCreate(
            company_id=test_company.id,
            title="Volunteer Study",
            description="No compensation",
            compensation_type=CompensationType.NONE
        )
        
        matching = MatchingService.create_matching_request(
            db, test_user.id, request_data
        )
        
        assert matching.compensation_type == CompensationType.NONE
        assert matching.compensation_amount is None
