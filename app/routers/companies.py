"""企業ルーター"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.company import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
)
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):
    """新規企業を作成"""
    # 既存チェック
    if CompanyService.get_company_by_email(db, company_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    if CompanyService.get_company_by_registration_number(
        db, company_data.business_registration_number
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business registration number already exists"
        )
    
    company = CompanyService.create_company(db, company_data)
    return company


@router.get("/", response_model=List[CompanyListResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """企業一覧を取得"""
    companies = CompanyService.list_companies(db, skip=skip, limit=limit)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    """企業情報を取得"""
    company = CompanyService.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    update_data: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """企業情報を更新"""
    company = CompanyService.update_company(db, company_id, update_data)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.patch("/{company_id}/verify")
def verify_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    """企業を検証（本人確認）"""
    company = CompanyService.verify_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return {"message": "Company verified", "verified_at": company.verified_at}


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    """企業を削除（論理削除）"""
    success = CompanyService.delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return None
