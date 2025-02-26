from typing import final
from warnings import catch_warnings

import jwt
import uuid
from fastapi import HTTPException
from passlib.exc import UnknownHashError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.model import User
from auth.repo import RepoUser
from auth.scheme import UserCreate
from auth.crypt.util import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.__db = db
        self._repo = RepoUser(db)

    def get_user(self, user_id: int):
        # user = self.__db.query(User).filter(User.id == user_id).first()
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, user_email: str):
        # user = self.__db.query(User).filter(User.email == user_email).first()
        user = self._repo.find_by_email(user_email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(self, user: UserCreate):
        hashKey = get_password_hash(user.password)
        gen_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, "wonik.com")
        print(hashKey)
        return self._repo.create(
            name=user.name, uuid=str(gen_uuid), email=user.email, key=hashKey
        )

    def verify_user(self, email, user_password):
        # user = self.__db.query(User).filter(User.email == email).first()
        user = self._repo.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        token = None
        try:
            if verify_password(user_password, user.key):
                # Todo : Create Token
                token = self.create_token(user.id)
                print(token)
            else:
                raise HTTPException(status_code=409, detail="Wrong Password")
        except UnknownHashError as e:
            err_msg = e.args[0]
            raise HTTPException(status_code=409, detail=err_msg)

        return {"token": token}

    def change_password(self, email, password, new_password):
        # user = self.__db.query(User).filter(User.email == email).first()
        user = self._repo.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            if verify_password(password, user.key):
                new_key = get_password_hash(new_password)
                self._repo.update_key_by_email(email=email, new_key=new_key)
                token = self.create_token(user.id)
                return True
            else:
                raise HTTPException(status_code=409, detail="password verify failed")
        except IntegrityError as e:
            self.__db.rollback()
            err_msg = e.args[0]
            raise HTTPException(
                status_code=409,
                detail="unknown error password change",
            )
        except UnknownHashError as e:
            self.__db.rollback()
            err_mag = e.args[0]
            raise HTTPException(
                status_code=409,
                detail=err_mag,
            )

    def create_token(self, user_id) -> str:
        return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")
