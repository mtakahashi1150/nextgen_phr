"""企業エンドポイントテスト"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate


class TestCompanyCreation:
    """企業作成テスト"""
    
    def test_create_company_success(self, client):
        """正常な企業作成"""
        company_data = {
            "name": "Health Research Corp",
            "email": "info@healthresearch.com",
            "business_registration_number": "BR-2024-001",
            "phone": "+81-90-1234-5678",
            "address": "Tokyo, Japan",
            "industry": "Healthcare Research",
            "description": "Leading healthcare research company",
            "password": "SecurePassword123!"
        }
        
        response = client.post("/companies/", json=company_data)
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == company_data["name"]
        assert data["email"] == company_data["email"]
        assert data["verified"] == False
        assert data["is_active"] == True
    
    def test_create_company_duplicate_email(self, client):
        """重複メールアドレスでの企業作成失敗"""
        company_data1 = {
            "name": "Company 1",
            "email": "same@email.com",
            "business_registration_number": "BR-001",
            "password": "Pass123!"
        }
        company_data2 = {
            "name": "Company 2",
            "email": "same@email.com",
            "business_registration_number": "BR-002",
            "password": "Pass123!"
        }
        
        response1 = client.post("/companies/", json=company_data1)
        assert response1.status_code == 201
        
        response2 = client.post("/companies/", json=company_data2)
        assert response2.status_code == 409
        assert "already registered" in response2.json()["detail"]
    
    def test_create_company_duplicate_registration(self, client):
        """重複事業登録番号でのエラー"""
        company_data1 = {
            "name": "Company 1",
            "email": "company1@email.com",
            "business_registration_number": "BR-SAME",
            "password": "Pass123!"
        }
        company_data2 = {
            "name": "Company 2",
            "email": "company2@email.com",
            "business_registration_number": "BR-SAME",
            "password": "Pass123!"
        }
        
        response1 = client.post("/companies/", json=company_data1)
        assert response1.status_code == 201
        
        response2 = client.post("/companies/", json=company_data2)
        assert response2.status_code == 409
    
    def test_create_company_invalid_email(self, client):
        """無効なメールアドレス"""
        company_data = {
            "name": "Invalid Email Co",
            "email": "invalid-email-format",
            "business_registration_number": "BR-2024-001",
            "password": "Pass123!"
        }
        
        response = client.post("/companies/", json=company_data)
        assert response.status_code == 422


class TestCompanyRetrieval:
    """企業取得テスト"""
    
    def test_list_companies(self, client):
        """企業一覧取得"""
        # テストデータ作成
        for i in range(3):
            company_data = CompanyCreate(
                name=f"Company {i}",
                email=f"company{i}@email.com",
                business_registration_number=f"BR-{i:03d}",
                password="Pass123!"
            )
            CompanyService.create_company(db, company_data)
        
        response = client.get("/companies/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_get_company_by_id(self, client):
        """企業情報取得"""
        company_data = CompanyCreate(
            name="Get Test Company",
            email="gettest@email.com",
            business_registration_number="BR-GET-001",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        response = client.get(f"/companies/{company.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test Company"
        assert data["id"] == company.id
    
    def test_get_nonexistent_company(self, client):
        """存在しない企業の取得"""
        response = client.get("/companies/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestCompanyUpdate:
    """企業更新テスト"""
    
    def test_update_company(self, client):
        """企業情報更新"""
        company_data = CompanyCreate(
            name="Original Name",
            email="original@email.com",
            business_registration_number="BR-UPDATE-001",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        update_data = {
            "name": "Updated Name",
            "address": "New Address"
        }
        response = client.put(f"/companies/{company.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["address"] == "New Address"


class TestCompanyVerification:
    """企業検証テスト"""
    
    def test_verify_company(self, client):
        """企業を検証"""
        company_data = CompanyCreate(
            name="Verify Test",
            email="verify@email.com",
            business_registration_number="BR-VERIFY-001",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        response = client.patch(f"/companies/{company.id}/verify")
        assert response.status_code == 200
        data = response.json()
        assert "verified_at" in data
        assert data["message"] == "Company verified"


class TestCompanyDeletion:
    """企業削除テスト（論理削除）"""
    
    def test_delete_company(self, client):
        """企業を削除（論理削除）"""
        company_data = CompanyCreate(
            name="Delete Test",
            email="delete@email.com",
            business_registration_number="BR-DELETE-001",
            password="Pass123!"
        )
        company = CompanyService.create_company(db, company_data)
        
        response = client.delete(f"/companies/{company.id}")
        assert response.status_code == 204
        
        # 削除後、is_active = False になっていることを確認
        deleted_company = CompanyService.get_company(db, company.id)
        # 論理削除なので取得は失敗
        # (is_active=False のため list_companies では取得されない)
