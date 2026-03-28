"""同意ルーター"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.consent import (
    ConsentCreate, ConsentUpdate, ConsentResponse, AuditLogResponse
)
from app.services.consent_service import ConsentService
from app.services.auth_service import verify_token as get_current_user

router = APIRouter(prefix="/consents", tags=["consents"])


def get_client_ip(x_forwarded_for: Optional[str] = Header(None), x_real_ip: Optional[str] = Header(None)) -> str:
    """クライアント IP アドレスを取得"""
    return x_forwarded_for or x_real_ip or "unknown"


def get_user_agent(user_agent: Optional[str] = Header(None)) -> str:
    """User-Agent を取得"""
    return user_agent or "unknown"


@router.post("/", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def create_consent(
    consent_data: ConsentCreate,
    authorization: str = Header(None),
    client_ip: str = Depends(get_client_ip),
    user_agent: str = Depends(get_user_agent),
    db: Session = Depends(get_db)
):
    """同意を作成"""
    user_id = get_current_user(authorization) if authorization else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    consent = ConsentService.create_consent(
        db, user_id, consent_data.company_id, consent_data,
        user_ip=client_ip, user_agent=user_agent
    )
    return consent


@router.get("/user", response_model=List[ConsentResponse])
def list_user_consents(
    skip: int = 0,
    limit: int = 100,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """ユーザーの同意一覧を取得"""
    user_id = get_current_user(authorization) if authorization else None
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    consents = ConsentService.list_user_consents(db, user_id, skip=skip, limit=limit)
    return consents


@router.get("/company/{company_id}", response_model=List[ConsentResponse])
def list_company_consents(
    company_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """企業が受信した同意一覧（例：マッチング用）"""
    consents = ConsentService.list_company_consents(
        db, company_id, skip=skip, limit=limit
    )
    return consents


@router.get("/{consent_id}", response_model=ConsentResponse)
def get_consent(
    consent_id: str,
    db: Session = Depends(get_db)
):
    """同意情報を取得"""
    consent = ConsentService.get_consent(db, consent_id)
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found"
        )
    return consent


@router.patch("/{consent_id}", response_model=ConsentResponse)
def update_consent_status(
    consent_id: str,
    update_data: ConsentUpdate,
    client_ip: str = Depends(get_client_ip),
    user_agent: str = Depends(get_user_agent),
    db: Session = Depends(get_db)
):
    """同意ステータスを更新"""
    consent = ConsentService.update_consent_status(
        db, consent_id, update_data.status,
        user_ip=client_ip, user_agent=user_agent
    )
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found"
        )
    return consent


@router.patch("/{consent_id}/withdraw")
def withdraw_consent(
    consent_id: str,
    client_ip: str = Depends(get_client_ip),
    user_agent: str = Depends(get_user_agent),
    db: Session = Depends(get_db)
):
    """同意を撤回"""
    consent = ConsentService.withdraw_consent(
        db, consent_id, user_ip=client_ip, user_agent=user_agent
    )
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found"
        )
    return {"message": "Consent withdrawn", "status": consent.status}


@router.get("/{consent_id}/audit-logs", response_model=List[AuditLogResponse])
def get_consent_audit_logs(
    consent_id: str,
    db: Session = Depends(get_db)
):
    """同意の監査ログを取得（GDPR対応）"""
    logs = ConsentService.get_audit_logs(db, consent_id)
    return logs
