from typing import final
from warnings import catch_warnings

import jwt
import uuid
from fastapi import HTTPException
from passlib.exc import UnknownHashError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.model import User
from auth.repo import RepoUser
from auth.scheme import UserCreate
from auth.crypt.util import get_password_hash, verify_password


class UserService:
    def __init__(self, db: AsyncSession):
        self._repo = RepoUser(db)

    async def get_user(self, user_id: int):
        """Retrieves a user by ID."""
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_by_email(self, user_email: str):
        """Retrieves a user by email."""
        user = await self._repo.find_by_email(user_email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(self, user: UserCreate):
        """Creates a new user."""
        hashed_password = get_password_hash(user.password)
        generated_uuid = uuid.uuid1()
        print(hashed_password)
        return await self._repo.create(
            name=user.name,
            uuid=str(generated_uuid),
            email=user.email,
            key=hashed_password,
        )

    async def verify_user(self, email: str, user_password: str):
        """Verifies user credentials and generates a token."""
        user = await self._repo.find_by_email(email)
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

    async def change_password(self, email: str, password: str, new_password: str):
        """Changes a user's password."""
        user = await self._repo.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            if not verify_password(password, user.key):
                raise HTTPException(
                    status_code=409, detail="Password verification failed"
                )

            new_key = get_password_hash(new_password)
            await self._repo.update_key_by_email(email=email, new_key=new_key)
            token = self.create_token(user.id)
            return True

        except Exception as e:
            raise HTTPException(
                status_code=409, detail="Unknown error during password change"
            )

    def create_token(self, user_id: int) -> str:
        """Creates a JWT token for the user."""
        return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")
