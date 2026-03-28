"""企業サービス"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
import uuid
from datetime import datetime
from app.services.auth_service import AuthService


class CompanyService:
    """企業管理サービス"""
    
    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate) -> Company:
        """企業を作成"""
        password_hash = AuthService.hash_password(company_data.password)
        
        company = Company(
            id=str(uuid.uuid4()),
            name=company_data.name,
            email=company_data.email,
            business_registration_number=company_data.business_registration_number,
            phone=company_data.phone,
            address=company_data.address,
            description=company_data.description,
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def get_company(db: Session, company_id: str) -> Company:
        """企業を取得"""
        query = select(Company).where(Company.id == company_id)
        return db.execute(query).scalar_one_or_none()
    
    @staticmethod
    def get_company_by_email(db: Session, email: str) -> Company:
        """メールアドレスで企業を取得"""
        query = select(Company).where(Company.email == email)
        return db.execute(query).scalar_one_or_none()
    
    @staticmethod
    def get_company_by_registration_number(db: Session, registration_number: str) -> Company:
        """事業登録番号で企業を取得"""
        query = select(Company).where(
            Company.business_registration_number == registration_number
        )
        return db.execute(query).scalar_one_or_none()
    
    @staticmethod
    def list_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
        """企業一覧を取得"""
        query = select(Company).where(Company.is_active == True).offset(skip).limit(limit)
        return db.execute(query).scalars().all()
    
    @staticmethod
    def update_company(db: Session, company_id: str, update_data: CompanyUpdate) -> Company:
        """企業を更新"""
        company = CompanyService.get_company(db, company_id)
        if not company:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(company, key, value)
        
        company.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def verify_company(db: Session, company_id: str) -> Company:
        """企業を検証"""
        company = CompanyService.get_company(db, company_id)
        if not company:
            return None
        
        company.verified = True
        company.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def delete_company(db: Session, company_id: str) -> bool:
        """企業を削除（論理削除）"""
        company = CompanyService.get_company(db, company_id)
        if not company:
            return False
        
        company.is_active = False
        company.updated_at = datetime.utcnow()
        db.commit()
        return True
