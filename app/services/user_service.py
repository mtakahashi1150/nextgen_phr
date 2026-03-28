"""ユーザー管理サービス"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import AuthService


class UserService:
    """ユーザー管理サービス"""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """ユーザーを作成"""
        # メールアドレスが既に存在するか確認
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise ValueError(f"Email {user_create.email} already registered")
        
        # パスワードをハッシュ化
        hashed_password = AuthService.hash_password(user_create.password)
        
        # 新規ユーザーを作成
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            name=user_create.name,
            date_of_birth=user_create.date_of_birth,
            gender=user_create.gender,
            address=user_create.address,
            phone=user_create.phone
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """IDでユーザーを取得"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """全ユーザーを取得"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """ユーザーを更新"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """ユーザーを削除"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        return True
    
    @staticmethod
    def toggle_user_active(db: Session, user_id: UUID) -> Optional[User]:
        """ユーザーのアクティブ状態を切り替え"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.is_active = not db_user.is_active
        db.commit()
        db.refresh(db_user)
        
        return db_user
