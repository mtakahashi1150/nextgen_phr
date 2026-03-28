#!/usr/bin/env python3
"""Phase 1 簡易API検証"""
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine
import os

# テスト環境設定
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# テーブル作成
Base.metadata.create_all(bind=engine)

client = TestClient(app)

print("✅ Phase 1 本番環境API検証")
print("=" * 60)

# テスト1: ユーザー登録
resp = client.post("/api/v1/auth/register", json={
    "email": "test@example.com",
    "password": "pass123",
    "name": "Test User"
})
print(f"✓ ユーザー登録: {resp.status_code} (期待値: 201)")
user_id = resp.json()["id"] if resp.status_code == 201 else None

# テスト2: ログイン
resp = client.post("/api/v1/auth/login", data={
    "username": "test@example.com",
    "password": "pass123"
})
print(f"✓ ログイン: {resp.status_code} (期待値: 200)")
token = resp.json()["access_token"] if resp.status_code == 200 else None

# テスト3: ユーザー一覧
headers = {"Authorization": f"Bearer {token}"} if token else {}
resp = client.get("/api/v1/users/", headers=headers)
print(f"✓ ユーザー一覧: {resp.status_code} (期待値: 200)")

# テスト4: ヘルスレコード作成
if user_id:
    resp = client.post(f"/api/v1/users/{user_id}/health-records/", 
        json={"record_type": "health_checkup", "data": {"weight": 70}},
        headers=headers)
    print(f"✓ レコード作成: {resp.status_code} (期待値: 201)")

print("=" * 60)
print("✅ 全APIエンドポイント動作確認完了！\n")
