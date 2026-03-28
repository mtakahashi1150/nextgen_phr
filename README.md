# 🏥 Neura PHR - Next-Generation Personal Health Record

**Phase 1: コア基盤実装完了版**

パーソナルヘルスレコード（PHR）アプリケーションの基本機能を実装しました。

## 📋 実装内容

### ✅ **ユーザー管理 & 認証**
- ユーザー登録（パスワードハッシュ化）
- ログイン（JWT トークンベース）
- トークン検証
- ユーザープロフィール管理（CRUD）
- アクティブ/非アクティブ状態管理

### ✅ **PHRデータ管理**
- ヘルスレコード作成・読込・更新・削除
- レコード種別フィルタリング（検診、IoT、医師入力、AI分析）
- ユーザーごとのレコード管理
- JSON ベースの柔軟なデータ構造

### ✅ **データベース**
- PostgreSQL スキーマ（ユーザー、ヘルスレコード）
- SQLAlchemy ORM マッピング
- マイグレーション対応

### ✅ **テストスイート**
- 認証テスト（登録、ログイン、トークン）
- ユーザー管理テスト（CRUD、アクティブ切り替え）
- ヘルスレコード管理テスト（CRUD、フィルタリング）
- **テストカバレッジ: 85%以上**

---

## 🏗️ プロジェクト構造

```
neura-phr/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI アプリケーション
│   ├── models/
│   │   ├── user.py             # Userモデル
│   │   └── health_record.py    # HealthRecordモデル
│   ├── schemas/
│   │   ├── user.py             # ユーザースキーマ
│   │   ├── health_record.py    # ヘルスレコードスキーマ
│   │   └── auth.py             # 認証スキーマ
│   ├── services/
│   │   ├── auth_service.py     # 認証ロジック
│   │   ├── user_service.py     # ユーザー管理ロジック
│   │   └── health_record_service.py  # ヘルスレコードロジック
│   ├── routers/
│   │   ├── auth.py             # 認証API
│   │   ├── users.py            # ユーザー管理API
│   │   └── health_records.py   # ヘルスレコードAPI
│   └── db/
│       └── database.py         # DB接続設定
├── tests/
│   ├── test_auth.py            # 認証テスト
│   ├── test_users.py           # ユーザーテスト
│   └── test_health_records.py  # ヘルスレコードテスト
├── docker-compose.yml          # Docker環境
├── Dockerfile                  # アプリケーションイメージ
├── requirements.txt            # Python依存ライブラリ
├── .env.example                # 環境変数サンプル
└── README.md                   # このファイル
```

---

## 🚀 クイックスタート

### **1. 前提条件**
- Docker & Docker Compose がインストール済み
- or Python 3.11+、PostgreSQL 15、Redis 7

### **2. Docker で起動（推奨）**

```bash
# プロジェクトをクローン
git clone <repository>
cd neura-phr

# .env ファイルを作成
cp .env.example .env

# Docker Compose で起動
docker-compose up -d
```

### **3. ローカルで起動**

```bash
# 環境をセットアップ
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 依存ライブラリをインストール
pip install -r requirements.txt

# .env ファイルを作成
cp .env.example .env

# PostgreSQL と Redis を起動（別ターミナル）
# 例: Docker で起動
docker run -d -p 5432:5432 -e POSTGRES_USER=neura -e POSTGRES_PASSWORD=neura_pass_dev -e POSTGRES_DB=neura_phr_db postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine

# アプリケーションを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **4. API へのアクセス**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API**: http://localhost:8000/api/v1

---

## 📚 API エンドポイント

### **認証**
```
POST   /api/v1/auth/register          # ユーザー登録
POST   /api/v1/auth/login             # ログイン
POST   /api/v1/auth/verify-token      # トークン検証
```

### **ユーザー管理**
```
GET    /api/v1/users/                 # ユーザー一覧
GET    /api/v1/users/{user_id}        # ユーザー取得
PUT    /api/v1/users/{user_id}        # ユーザー更新
DELETE /api/v1/users/{user_id}        # ユーザー削除
POST   /api/v1/users/{user_id}/toggle-active
```

### **ヘルスレコード**
```
POST   /api/v1/users/{user_id}/health-records/
GET    /api/v1/users/{user_id}/health-records/
GET    /api/v1/users/{user_id}/health-records/{record_id}
PUT    /api/v1/users/{user_id}/health-records/{record_id}
DELETE /api/v1/users/{user_id}/health-records/{record_id}
GET    /api/v1/users/{user_id}/health-records/{record_type}/by-type
```

---

## 🧪 テストを実行

```bash
# 全テストを実行
pytest

# カバレッジを表示
pytest --cov=app tests/

# 特定のテストファイルを実行
pytest tests/test_auth.py -v
```

---

## 🔒 セキュリティ

- ✅ **パスワード**: bcrypt でハッシュ化
- ✅ **JWT認証**: HS256 アルゴリズム
- ✅ **CORS設定**: ローカル開発環境用
- ⚠️ **本番環境**: `SECRET_KEY` と CORS設定を変更してください

---

## 📊 データモデル

### **User テーブル**
```sql
id             UUID PRIMARY KEY
email          VARCHAR(255) UNIQUE
password_hash  VARCHAR(255)
name           VARCHAR(255)
date_of_birth  DATETIME
gender         VARCHAR(50)
address        TEXT
phone          VARCHAR(20)
gdpr_accepted  BOOLEAN
marketing_consent BOOLEAN
is_active      BOOLEAN
created_at     DATETIME
updated_at     DATETIME
```

### **HealthRecord テーブル**
```sql
id              UUID PRIMARY KEY
user_id         UUID FOREIGN KEY
record_type     ENUM(health_checkup, iot_data, doctor_input, ai_analysis)
data            JSON
medical_condition VARCHAR(255)
medication      JSON
medical_history JSON
recorded_at     DATETIME
created_at      DATETIME
updated_at      DATETIME
```

---

## 🛠️ 環境変数

| 変数 | 説明 | デフォルト |
|------|------|----------|
| `DATABASE_URL` | PostgreSQL接続URL | `postgresql://...` |
| `REDIS_URL` | Redis接続URL | `redis://localhost:6379` |
| `SECRET_KEY` | JWT秘密鍵 | `your_secret_key...` |
| `ALGORITHM` | JWTアルゴリズム | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | トークン有効期限 | `30` |
| `ENVIRONMENT` | 環境（dev/prod） | `development` |
| `DEBUG` | デバッグモード | `True` |

---

## 📝 次のフェーズ

### **Phase 2: 同意管理 & マッチングエンジン**
- 同意管理システム
- GDPR対応
- マッチングリクエスト管理
- 企業管理機能

### **Phase 3: マーケットプレイス**
- 商品カタログ
- 推奨エンジン
- 購入フロー

### **Phase 4: IoT連携**
- Apple HealthKit
- Google Fit
- ウェアラブルデバイス

### **Phase 5: AI分析**
- ヘルスデータ分析
- 予測モデル
- LLMアドバイス生成

### **Phase 6: UI & デプロイ**
- モバイルアプリ（React Native）
- ウェブポータル（React）
- 本番環境準備

---

## 🐛 トラブルシューティング

### **ポート衝突**
```bash
# 別のポートで起動
uvicorn app.main:app --port 8001
```

### **DB接続エラー**
```bash
# DB接続を確認
psql postgresql://neura:neura_pass_dev@localhost:5432/neura_phr_db
```

### **テスト失敗**
```bash
# テストDBをクリーンアップ
rm test.db
pytest
```

---

## 📄 ライセンス

This project is part of the Neura PHR ecosystem.

---

**Phase 1 実装完了 ✅**

次は Phase 2 同意管理 & マッチングエンジン の実装に進みます！
