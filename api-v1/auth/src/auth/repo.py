from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.model import User


class RepoUser(object):
    def __init__(self, DBSession: AsyncSession):
        self._session = DBSession

    async def create(self, name: str, uuid: str, email: str, key: str):
        new_user = User(name=name, uuid=uuid, email=email, key=key)
        try:
            self._session.add(new_user)
            await self._session.commit()
            await self._session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await self._session.rollback()
            err_msg = str(e.args[0])
            print(err_msg)
            if "Duplicate entry" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail="email already exists (%s)" % email,
                )
            else:
                raise HTTPException(
                    status_code=409,
                    detail="unknown error adding user",
                )

    async def find_by_id(self, user_id: int):
        user = await self._session.get(User, user_id)
        return user

    async def find_by_uuid(self, user_uuid: str):
        user = await self._session.scalar(
            self._session.query(User).filter(User.uuid == user_uuid)
        )
        return user

    async def find_by_email(self, email: str):
        user = await self._session.scalar(
            self._session.query(User).filter(User.email == email)
        )
        return user

    async def update_key_by_email(self, email: str, new_key: str):
        await self._session.execute(
            self._session.query(User).filter_by(email=email).update({"key": new_key})
        )
        await self._session.commit()
