"""認証スキーマ"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenRequest(BaseModel):
    """トークンリクエスト"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """トークン応答"""
    access_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """リフレッシュトークンリクエスト"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """パスワードリセットリクエスト"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """パスワードリセット確認"""
    token: str
    new_password: str
