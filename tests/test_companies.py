"""企業サービスレイアーテスト"""
import pytest
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate


class TestCompanyService:
    """企業サービスロジック"""
    
    def test_create_company(self, db):
        """企業作成"""
        company_data = CompanyCreate(
            name="Test Lab",
            email="test@lab.com",
            business_registration_number="BR-001",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        assert company.id is not None
        assert company.name == "Test Lab"
        assert company.verified == False
        assert company.is_active == True
    
    def test_get_company(self, db):
        """企業取得"""
        company_data = CompanyCreate(
            name="Get Test",
            email="get@test.com",
            business_registration_number="BR-002",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        retrieved = CompanyService.get_company(db, company.id)
        
        assert retrieved.name == "Get Test"
    
    def test_get_company_by_email(self, db):
        """メールアドレスで企業取得"""
        company_data = CompanyCreate(
            name="Email Test",
            email="unique@email.com",
            business_registration_number="BR-003",
            password="Pass123!"
        )
        CompanyService.create_company(db, company_data)
        company = CompanyService.get_company_by_email(db, "unique@email.com")
        
        assert company.name == "Email Test"
    
    def test_list_companies(self, db):
        """企業一覧"""
        for i in range(3):
            company_data = CompanyCreate(
                name=f"Company {i}",
                email=f"company{i}@test.com",
                business_registration_number=f"BR-{i:03d}",
                password="Pass123!"
            )
            CompanyService.create_company(db, company_data)
        
        companies = CompanyService.list_companies(db)
        assert len(companies) >= 3
    
    def test_update_company(self, db):
        """企業更新"""
        company_data = CompanyCreate(
            name="Original",
            email="original@test.com",
            business_registration_number="BR-004",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        update_data = CompanyUpdate(name="Updated Name")
        updated = CompanyService.update_company(db, company.id, update_data)
        
        assert updated.name == "Updated Name"
    
    def test_verify_company(self, db):
        """企業検証"""
        company_data = CompanyCreate(
            name="Verify Test",
            email="verify@test.com",
            business_registration_number="BR-005",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        verified = CompanyService.verify_company(db, company.id)
        assert verified.verified == True
        assert verified.verified_at is not None
    
    def test_delete_company(self, db):
        """企業削除"""
        company_data = CompanyCreate(
            name="Delete Test",
            email="delete@test.com",
            business_registration_number="BR-006",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        success = CompanyService.delete_company(db, company.id)
        assert success == True
