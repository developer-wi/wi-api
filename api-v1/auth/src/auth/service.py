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
        """Retrieves a user by ID."""
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, user_email: str):
        """Retrieves a user by email."""
        user = self._repo.find_by_email(user_email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(self, user: UserCreate):
        """Creates a new user."""
        hashed_password = get_password_hash(user.password)
        generated_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, "wonik.com")
        print(hashed_password)
        return self._repo.create(
            name=user.name,
            uuid=str(generated_uuid),
            email=user.email,
            key=hashed_password,
        )

    def verify_user(self, email: str, user_password: str):
        """Verifies user credentials and generates a token."""
        user = self._repo.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            if not verify_password(user_password, user.key):
                raise HTTPException(status_code=409, detail="Wrong Password")

            token = self.create_token(user.id)
            print(token)
            return {"token": token}

        except UnknownHashError as e:
            raise HTTPException(status_code=409, detail=str(e))

    def change_password(self, email: str, password: str, new_password: str):
        """Changes a user's password."""
        user = self._repo.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            if not verify_password(password, user.key):
                raise HTTPException(
                    status_code=409, detail="Password verification failed"
                )

            new_key = get_password_hash(new_password)
            self._repo.update_key_by_email(email=email, new_key=new_key)
            token = self.create_token(user.id)
            return True

        except IntegrityError as e:
            self.__db.rollback()
            raise HTTPException(
                status_code=409, detail="Unknown error during password change"
            )
        except UnknownHashError as e:
            self.__db.rollback()
            raise HTTPException(status_code=409, detail=str(e))

    def create_token(self, user_id: int) -> str:
        """Creates a JWT token for the user."""
        return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")
