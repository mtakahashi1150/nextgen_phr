"""マッチングリクエストルーター"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.matching import (
    MatchingRequestCreate, MatchingRequestUpdate, MatchingRequestResponse, MatchingListResponse
)
from app.services.matching_service import MatchingService
from app.services.auth_service import verify_token as get_current_user

router = APIRouter(prefix="/matching-requests", tags=["matching"])


@router.post("/", response_model=MatchingRequestResponse, status_code=status.HTTP_201_CREATED)
def send_matching_request(
    request_data: MatchingRequestCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """マッチングリクエストを送信"""
    user_id = get_current_user(authorization) if authorization else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    matching = MatchingService.create_matching_request(
        db, user_id, request_data
    )
    return matching


@router.get("/sent", response_model=List[MatchingListResponse])
def list_sent_requests(
    skip: int = 0,
    limit: int = 100,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """ユーザーが送信したマッチングリクエスト一覧"""
    user_id = get_current_user(authorization) if authorization else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    requests = MatchingService.list_sent_requests(
        db, user_id, skip=skip, limit=limit
    )
    return requests


@router.get("/received/{company_id}", response_model=List[MatchingListResponse])
def list_received_requests(
    company_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """企業が受信したマッチングリクエスト一覧"""
    requests = MatchingService.list_received_requests(
        db, company_id, skip=skip, limit=limit
    )
    return requests


@router.get("/{request_id}", response_model=MatchingRequestResponse)
def get_matching_request(
    request_id: str,
    db: Session = Depends(get_db)
):
    """マッチングリクエスト詳細を取得"""
    matching = MatchingService.get_matching_request(db, request_id)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching request not found"
        )
    
    # 閲覧済みにマーク
    MatchingService.mark_as_viewed(db, request_id)
    
    return matching


@router.patch("/{request_id}", response_model=MatchingRequestResponse)
def update_matching_request(
    request_id: str,
    update_data: MatchingRequestUpdate,
    db: Session = Depends(get_db)
):
    """マッチングリクエストを更新（受理/拒否）"""
    matching = MatchingService.get_matching_request(db, request_id)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching request not found"
        )
    
    # ステータスに応じた処理
    if update_data.status.value == "accepted":
        matching = MatchingService.accept_request(
            db, request_id, update_data.response_reason
        )
    elif update_data.status.value == "rejected":
        matching = MatchingService.reject_request(
            db, request_id, update_data.response_reason
        )
    
    return matching


@router.post("/{request_id}/accept", response_model=MatchingRequestResponse)
def accept_matching_request(
    request_id: str,
    reason: str = None,
    db: Session = Depends(get_db) 
):
    """マッチングリクエストを受理"""
    matching = MatchingService.accept_request(db, request_id, reason)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching request not found"
        )
    return matching


@router.post("/{request_id}/reject", response_model=MatchingRequestResponse)
def reject_matching_request(
    request_id: str,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """マッチングリクエストを拒否"""
    matching = MatchingService.reject_request(db, request_id, reason)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching request not found"
        )
    return matching


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_matching_request(
    request_id: str,
    db: Session = Depends(get_db)
):
    """マッチングリクエストを撤回"""
    matching = MatchingService.withdraw_request(db, request_id)
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matching request not found"
        )
    return None
