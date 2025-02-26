from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.scheme import UserVerify, UserNewPassword
from database.app import Master_Session, Slave_Session, Master_Base
from auth.service import UserCreate, UserService


def get_db(read_only: bool = False):
    # Base.metadata.create_all(bind=engine)
    if read_only:
        db = Slave_Session()
    else:
        db = Master_Session()
    try:
        yield db
    finally:
        db.close()


router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.create_user(user)
    return user


@router_auth.post("/verify")
def verify(user: UserVerify, db: Session = Depends(get_db)):
    user_service = UserService(db)
    token = user_service.verify_user(user.email, user.password)
    return token


@router_auth.get("/")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if str(type(user)) == "<class 'fastapi.exceptions.HTTPException'>":
        raise user
    return user


@router_auth.get("/email")
def get_user_by_email(user_email: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_email)
    print(str(type(user)))
    if str(type(user)) == "<class 'fastapi.exceptions.HTTPException'>":
        raise user
    return user


@router_auth.post("/password/change")
def change_password(user: UserNewPassword, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user_service.change_password(
        email=user.email, password=user.password, new_password=user.new_password
    )
    return {"result": "success"}
