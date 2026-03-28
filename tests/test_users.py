"""ユーザー管理テスト"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

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


def test_list_users():
    """ユーザー一覧取得テスト"""
    create_test_user()
    
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == "testuser@example.com"


def test_get_user():
    """ユーザー取得テスト"""
    user = create_test_user()
    user_id = user["id"]
    
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"


def test_get_nonexistent_user():
    """非存在ユーザー取得テスト"""
    response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_user():
    """ユーザー更新テスト"""
    user = create_test_user()
    user_id = user["id"]
    
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={
            "name": "Updated User",
            "phone": "1234567890"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["phone"] == "1234567890"


def test_delete_user():
    """ユーザー削除テスト"""
    user = create_test_user()
    user_id = user["id"]
    
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204
    
    # 削除後、取得できないことを確認
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 404


def test_toggle_user_active():
    """ユーザーアクティブ状態切り替えテスト"""
    user = create_test_user()
    user_id = user["id"]
    
    # 初期状態は active = True
    assert user["is_active"] == True
    
    # トグル
    response = client.post(f"/api/v1/users/{user_id}/toggle-active")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False
    
    # もう一度トグル
    response = client.post(f"/api/v1/users/{user_id}/toggle-active")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True
