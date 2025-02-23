from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.app import SessionLocal
from auth.service import UserCreate, UserService


def get_db():
    # Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router_auth = APIRouter(prefix="/auth")


@router_auth.post("/create", tags=["auth"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user)


@router_auth.get("/", tags=["auth"])
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if str(type(user)) == "<class 'fastapi.exceptions.HTTPException'>":
        raise user
    return user


@router_auth.get("/email", tags=["auth"])
def get_user_by_email(user_email: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_email)
    if str(type(user)) == "<class 'fastapi.exceptions.HTTPException'>":
        raise user
    return user
