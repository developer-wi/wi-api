from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.scheme import AuthVerify, AuthNewPassword, AuthCreate
from databaselib.mysql.app import get_db
from auth.service import AuthService


router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/create")
async def create_auth(auth: AuthCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    auth = await auth_service.create_auth(auth)
    return auth


@router_auth.post("/verify")
async def verify(auth: AuthVerify, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    token = await auth_service.verify_auth(auth.email, auth.password)
    return token


@router_auth.get("/")
async def get_auth_by_id(auth_id: int, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    auth = await auth_service.get_auth(auth_id)
    return auth


@router_auth.get("/email")
async def get_auth_by_email(auth_email: str, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    auth = await auth_service.get_auth_by_email(auth_email)
    return auth


@router_auth.post("/password/change")
async def change_password(auth: AuthNewPassword, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    result = await auth_service.change_password(
        email=auth.email, password=auth.password, new_password=auth.new_password
    )
    return {"result": "success"}
