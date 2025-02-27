from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.scheme import UserVerify, UserNewPassword, UserCreate
from database.app import get_db
from auth.service import UserService


router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/create")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.create_user(user)
    return user


@router_auth.post("/verify")
async def verify(user: UserVerify, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    token = await user_service.verify_user(user.email, user.password)
    return token


@router_auth.get("/")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    return user


@router_auth.get("/email")
async def get_user_by_email(user_email: str, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(user_email)
    return user


@router_auth.post("/password/change")
async def change_password(user: UserNewPassword, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    result = await user_service.change_password(
        email=user.email, password=user.password, new_password=user.new_password
    )
    return {"result": "success"}
