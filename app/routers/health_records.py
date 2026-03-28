"""ヘルスレコードAPIルーター"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.schemas.health_record import HealthRecordResponse, HealthRecordCreate, HealthRecordUpdate, HealthRecordListResponse
from app.services.health_record_service import HealthRecordService
from app.services.user_service import UserService
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/users/{user_id}/health-records", tags=["health_records"])


@router.get("/", response_model=List[HealthRecordListResponse])
async def list_health_records(user_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ユーザーのヘルスレコード一覧を取得"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    records = HealthRecordService.get_user_health_records(db, user_id, skip=skip, limit=limit)
    return records


@router.post("/", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_health_record(
    user_id: UUID,
    record_create: HealthRecordCreate,
    db: Session = Depends(get_db)
):
    """ヘルスレコードを作成"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    record = HealthRecordService.create_health_record(db, user_id, record_create)
    return record


@router.get("/{record_id}", response_model=HealthRecordResponse)
async def get_health_record(user_id: UUID, record_id: UUID, db: Session = Depends(get_db)):
    """ヘルスレコードを取得"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    record = HealthRecordService.get_health_record_by_id(db, record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    return record


@router.put("/{record_id}", response_model=HealthRecordResponse)
async def update_health_record(
    user_id: UUID,
    record_id: UUID,
    record_update: HealthRecordUpdate,
    db: Session = Depends(get_db)
):
    """ヘルスレコードを更新"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # レコードのオーナーシップを確認
    record = HealthRecordService.get_health_record_by_id(db, record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    updated_record = HealthRecordService.update_health_record(db, record_id, record_update)
    return updated_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_record(user_id: UUID, record_id: UUID, db: Session = Depends(get_db)):
    """ヘルスレコードを削除"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # レコードのオーナーシップを確認
    record = HealthRecordService.get_health_record_by_id(db, record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    
    success = HealthRecordService.delete_health_record(db, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete health record")


@router.get("/{record_type}/by-type", response_model=List[HealthRecordListResponse])
async def get_health_records_by_type(
    user_id: UUID,
    record_type: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """レコード種別でフィルタリング"""
    # ユーザーが存在するか確認
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    records = HealthRecordService.get_user_health_records_by_type(
        db, user_id, record_type, skip=skip, limit=limit
    )
    return records
