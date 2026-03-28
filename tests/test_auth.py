"""認証テスト"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
import os

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


def test_register_user():
    """ユーザー登録テスト"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "name": "Test User",
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "phone": None
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert "password" not in data


def test_register_duplicate_email():
    """重複メールアドレス登録テスト"""
    # 最初のユーザーを登録
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    
    # 同じメールアドレスで登録を試みる
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass456",
            "name": "Another User"
        }
    )
    assert response.status_code == 400


def test_login_success():
    """ログイン成功テスト"""
    # ユーザーを登録
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    
    # ログイン
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password():
    """ログイン失敗（パスワード間違い）テスト"""
    # ユーザーを登録
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    
    # 間違ったパスワードでログイン
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_login_nonexistent_user():
    """ログイン失敗（未存在ユーザー）テスト"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 401
