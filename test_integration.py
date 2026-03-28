#!/usr/bin/env python3
"""Phase 1 API統合テスト"""
import os
import sys
from fastapi.testclient import TestClient

# 環境設定
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# アプリケーション初期化
from app.main import app
from app.db.database import Base, engine, get_db

# テスト用テーブル作成
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_api_endpoints():
    """API統合テスト"""
    print("\n" + "="*60)
    print("🧪 Phase 1 API統合テスト")
    print("="*60)
    
    # 1. ユーザー登録
    print("\n1️⃣ ユーザー登録テスト...")
    register_data = {
        "email": "john@example.com",
        "password": "password123",
        "name": "John Doe",
        "date_of_birth": None,
        "gender": "male",
        "address": "Tokyo, Japan",
        "phone": "09012345678"
    }
    resp = client.post("/api/v1/auth/register", json=register_data)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 201:
        user_data = resp.json()
        user_id = user_data["id"]
        print(f"   ✅ ユーザー登録成功: ID={user_id}")
    else:
        print(f"   ❌ 失敗: {resp.text}")
        return
    
    # 2. ログイン
    print("\n2️⃣ ログインテスト...")
    login_data = {
        "username": "john@example.com",
        "password": "password123"
    }
    resp = client.post("/api/v1/auth/login", data=login_data)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data["access_token"]
        print(f"   ✅ ログイン成功: Token={token[:20]}...")
    else:
        print(f"   ❌ 失敗: {resp.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. ユーザー情報取得
    print("\n3️⃣ ユーザー情報取得テスト...")
    resp = client.get(f"/api/v1/users/{user_id}", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ ユーザー取得成功: {resp.json()['name']}")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 4. ヘルスレコード作成
    print("\n4️⃣ ヘルスレコード作成テスト...")
    record_data = {
        "record_type": "health_checkup",
        "data": {
            "height": 175,
            "weight": 70,
            "blood_pressure": "120/80",
            "cholesterol": 180
        },
        "medical_condition": "Healthy",
        "medication": ["Vitamin D"],
        "medical_history": ["None"]
    }
    resp = client.post(f"/api/v1/users/{user_id}/health-records/", json=record_data, headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 201:
        record = resp.json()
        record_id = record["id"]
        print(f"   ✅ レコード作成成功: ID={record_id}")
    else:
        print(f"   ❌ 失敗: {resp.text}")
        return
    
    # 5. ヘルスレコード一覧取得
    print("\n5️⃣ ヘルスレコード一覧取得テスト...")
    resp = client.get(f"/api/v1/users/{user_id}/health-records/", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        records = resp.json()
        print(f"   ✅ レコード取得成功: {len(records)}件")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 6. ヘルスレコード更新
    print("\n6️⃣ ヘルスレコード更新テスト...")
    update_data = {
        "medical_condition": "Excellent health condition"
    }
    resp = client.put(f"/api/v1/users/{user_id}/health-records/{record_id}", json=update_data, headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ レコード更新成功")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 7. タイプ別フィルタリング
    print("\n7️⃣ タイプ別フィルタリングテスト...")
    resp = client.get(f"/api/v1/users/{user_id}/health-records/health_checkup/by-type", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        records = resp.json()
        print(f"   ✅ フィルタリング成功: {len(records)}件")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 8. ユーザー一覧取得
    print("\n8️⃣ ユーザー一覧取得テスト...")
    resp = client.get("/api/v1/users/", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        users = resp.json()
        print(f"   ✅ ユーザー一覧取得成功: {len(users)}件")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 9. ユーザー更新
    print("\n9️⃣ ユーザー更新テスト...")
    update_user = {"name": "John Smith"}
    resp = client.put(f"/api/v1/users/{user_id}", json=update_user, headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ ユーザー更新成功")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 10. アクティブ状態切り替え
    print("\n🔟 アクティブ状態切り替えテスト...")
    resp = client.post(f"/api/v1/users/{user_id}/toggle-active", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ アクティブ状態切り替え成功")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 11. ヘルスレコード削除
    print("\n1️⃣1️⃣ ヘルスレコード削除テスト...")
    resp = client.delete(f"/api/v1/users/{user_id}/health-records/{record_id}", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 204:
        print(f"   ✅ レコード削除成功")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    # 12. ユーザー削除
    print("\n1️⃣2️⃣ ユーザー削除テスト...")
    resp = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    print(f"   ステータス: {resp.status_code}")
    if resp.status_code == 204:
        print(f"   ✅ ユーザー削除成功")
    else:
        print(f"   ❌ 失敗: {resp.text}")
    
    print("\n" + "="*60)
    print("✅ 全APIテスト完了！")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)
