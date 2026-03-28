"""FastAPI メインアプリケーション"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.routers import auth, users, health_records, companies, consents, matching_requests
import os

# FastAPIアプリケーションを作成
app = FastAPI(
    title="Neura PHR API",
    description="Next-Generation Personal Health Record Application",
    version="0.1.0"
)

# CORS設定
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health_records.router)
app.include_router(companies.router)
app.include_router(consents.router)
app.include_router(matching_requests.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "name": "Neura PHR API",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
