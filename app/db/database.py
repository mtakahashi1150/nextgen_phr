"""データベース設定"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# 環境変数からDATABASE_URLを取得
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neura:neura_pass_dev@localhost:5432/neura_phr_db"
)

# SQLAlchemy エンジン作成
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if os.getenv("ENVIRONMENT") == "testing" else None,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# セッション作成ファクトリ
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ORM基底クラス
Base = declarative_base()


def get_db():
    """データベースセッション依存関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
