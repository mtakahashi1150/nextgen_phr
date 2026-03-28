"""ヘルスレコードテスト"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from datetime import datetime

# テスト用DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_teardown():
    """各テスト前後の設定・クリーンアップ"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_test_user():
    """テスト用ユーザーを作成"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    return response.json()


def create_test_health_record(user_id):
    """テスト用ヘルスレコードを作成"""
    response = client.post(
        f"/api/v1/users/{user_id}/health-records/",
        json={
            "record_type": "health_checkup",
            "data": {
                "height": 175,
                "weight": 70,
                "blood_pressure": "120/80",
                "cholesterol": 180,
                "glucose": 95,
                "heart_rate": 72
            },
            "medical_condition": "Hypertension",
            "medication": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg"
                }
            ]
        }
    )
    return response.json()


def test_create_health_record():
    """ヘルスレコード作成テスト"""
    user = create_test_user()
    user_id = user["id"]
    
    response = client.post(
        f"/api/v1/users/{user_id}/health-records/",
        json={
            "record_type": "health_checkup",
            "data": {
                "height": 175,
                "weight": 70,
                "blood_pressure": "120/80"
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == user_id
    assert data["record_type"] == "health_checkup"
    assert data["data"]["height"] == 175


def test_list_user_health_records():
    """ユーザーのヘルスレコード一覧取得テスト"""
    user = create_test_user()
    user_id = user["id"]
    
    # 複数のレコードを作成
    create_test_health_record(user_id)
    create_test_health_record(user_id)
    
    response = client.get(f"/api/v1/users/{user_id}/health-records/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_health_record():
    """ヘルスレコード取得テスト"""
    user = create_test_user()
    user_id = user["id"]
    record = create_test_health_record(user_id)
    record_id = record["id"]
    
    response = client.get(f"/api/v1/users/{user_id}/health-records/{record_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == record_id
    assert data["record_type"] == "health_checkup"


def test_update_health_record():
    """ヘルスレコード更新テスト"""
    user = create_test_user()
    user_id = user["id"]
    record = create_test_health_record(user_id)
    record_id = record["id"]
    
    response = client.put(
        f"/api/v1/users/{user_id}/health-records/{record_id}",
        json={
            "medical_condition": "Updated Condition",
            "data": {
                "weight": 72
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["medical_condition"] == "Updated Condition"


def test_delete_health_record():
    """ヘルスレコード削除テスト"""
    user = create_test_user()
    user_id = user["id"]
    record = create_test_health_record(user_id)
    record_id = record["id"]
    
    response = client.delete(f"/api/v1/users/{user_id}/health-records/{record_id}")
    assert response.status_code == 204
    
    # 削除後、取得できないことを確認
    response = client.get(f"/api/v1/users/{user_id}/health-records/{record_id}")
    assert response.status_code == 404


def test_get_health_records_by_type():
    """レコード種別でフィルタリングテスト"""
    user = create_test_user()
    user_id = user["id"]
    
    # health_checkup レコードを作成
    create_test_health_record(user_id)
    
    # IoT レコードを作成
    client.post(
        f"/api/v1/users/{user_id}/health-records/",
        json={
            "record_type": "iot_data",
            "data": {"steps": 5000, "calories": 300}
        }
    )
    
    # health_checkup をフィルタリング
    response = client.get(
        f"/api/v1/users/{user_id}/health-records/health_checkup/by-type"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["record_type"] == "health_checkup"


def test_create_health_record_nonexistent_user():
    """非存在ユーザーへのレコード作成テスト"""
    response = client.post(
        "/api/v1/users/00000000-0000-0000-0000-000000000000/health-records/",
        json={
            "record_type": "health_checkup",
            "data": {"weight": 70}
        }
    )
    assert response.status_code == 404
