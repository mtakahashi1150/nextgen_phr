"""マッチングサービス"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.matching import MatchingRequest, MatchingStatus
from app.schemas.matching import MatchingRequestCreate, MatchingRequestUpdate
import uuid
from datetime import datetime, timedelta


class MatchingService:
    """マッチングリクエスト管理サービス"""
    
    @staticmethod
    def create_matching_request(
        db: Session,
        user_id: str,
        matching_data: MatchingRequestCreate
    ) -> MatchingRequest:
        """マッチングリクエストを作成"""
        # 30日後を有効期限に設定
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        matching = MatchingRequest(
            id=str(uuid.uuid4()),
            from_user_id=user_id,
            to_company_id=matching_data.company_id,
            status=MatchingStatus.SENT,
            title=matching_data.title,
            description=matching_data.description,
            health_conditions=matching_data.health_conditions,
            study_duration_days=matching_data.study_duration_days,
            compensation_type=matching_data.compensation_type,
            compensation_amount=matching_data.compensation_amount,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        db.add(matching)
        db.commit()
        db.refresh(matching)
        return matching
    
    @staticmethod
    def get_matching_request(db: Session, request_id: str) -> MatchingRequest:
        """マッチングリクエストを取得"""
        query = select(MatchingRequest).where(MatchingRequest.id == request_id)
        return db.execute(query).scalar_one_or_none()
    
    @staticmethod
    def list_sent_requests(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[MatchingRequest]:
        """ユーザーが送信したマッチングリクエスト一覧"""
        query = (
            select(MatchingRequest)
            .where(MatchingRequest.from_user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).scalars().all()
    
    @staticmethod
    def list_received_requests(
        db: Session,
        company_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[MatchingRequest]:
        """企業が受信したマッチングリクエスト一覧"""
        query = (
            select(MatchingRequest)
            .where(MatchingRequest.to_company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).scalars().all()
    
    @staticmethod
    def mark_as_viewed(db: Session, request_id: str) -> MatchingRequest:
        """リクエストを「閲覧済み」にマーク"""
        matching = MatchingService.get_matching_request(db, request_id)
        if not matching:
            return None
        
        if matching.status == MatchingStatus.SENT:
            matching.status = MatchingStatus.VIEWED
            matching.viewed_at = datetime.utcnow()
            matching.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(matching)
        return matching
    
    @staticmethod
    def accept_request(
        db: Session,
        request_id: str,
        reason: str = None
    ) -> MatchingRequest:
        """マッチングリクエストを受理"""
        matching = MatchingService.get_matching_request(db, request_id)
        if not matching:
            return None
        
        matching.status = MatchingStatus.ACCEPTED
        matching.responded_at = datetime.utcnow()
        matching.response_reason = reason
        matching.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(matching)
        return matching
    
    @staticmethod
    def reject_request(
        db: Session,
        request_id: str,
        reason: str = None
    ) -> MatchingRequest:
        """マッチングリクエストを拒否"""
        matching = MatchingService.get_matching_request(db, request_id)
        if not matching:
            return None
        
        matching.status = MatchingStatus.REJECTED
        matching.responded_at = datetime.utcnow()
        matching.response_reason = reason
        matching.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(matching)
        return matching
    
    @staticmethod
    def withdraw_request(db: Session, request_id: str) -> MatchingRequest:
        """マッチングリクエストを撤回"""
        matching = MatchingService.get_matching_request(db, request_id)
        if not matching:
            return None
        
        if matching.status in [MatchingStatus.SENT, MatchingStatus.VIEWED]:
            matching.status = MatchingStatus.WITHDRAWN
            matching.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(matching)
        
        return matching
    
    @staticmethod
    def check_expired_requests(db: Session) -> int:
        """有効期限切れのリクエストをマークする"""
        now = datetime.utcnow()
        query = (
            select(MatchingRequest)
            .where(
                (MatchingRequest.status == MatchingStatus.SENT) |
                (MatchingRequest.status == MatchingStatus.VIEWED)
            )
            .where(MatchingRequest.expires_at <= now)
        )
        expired_requests = db.execute(query).scalars().all()
        
        for matching in expired_requests:
            matching.status = MatchingStatus.EXPIRED
            matching.updated_at = datetime.utcnow()
        
        db.commit()
        return len(expired_requests)
