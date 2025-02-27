from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from auth.model import User


class RepoUser(object):
    def __init__(self, db: AsyncSession):
        self._session = db

    async def create(self, name: str, uuid: str, email: str, key: str):
        new_user = User(name=name, uuid=uuid, email=email, key=key)
        try:
            self._session.add(new_user)
            await self._session.commit()
            await self._session.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await self._session.rollback()
            if "Duplicate entry" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail=f"email already exists: {email}",
                )
            else:
                raise HTTPException(status_code=409, detail="unknown error adding user")
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def find_by_id(self, user_id: int):
        user = await self._session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def find_by_uuid(self, user_uuid: str):
        try:
            result = await self._session.execute(
                select(User).where(User.uuid == user_uuid)
            )
            user = result.scalar_one()
            return user
        except NoResultFound:
            raise HTTPException(
                status_code=404, detail=f"User not found for uuid: {user_uuid}"
            )
        except MultipleResultsFound:
            raise HTTPException(
                status_code=500,
                detail=f"Multiple users found for uuid: {user_uuid}",
            )
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def find_by_email(self, email: str):
        try:
            result = await self._session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one()
            return user
        except NoResultFound:
            raise HTTPException(
                status_code=404, detail=f"User not found for email: {email}"
            )
        except MultipleResultsFound:
            raise HTTPException(
                status_code=500,
                detail=f"Multiple users found for email: {email}",
            )
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def update_key_by_email(self, email: str, new_key: str):
        try:
            result = await self._session.execute(
                update(User).where(User.email == email).values(key=new_key)
            )
            if result.rowcount == 0 or not result.rowcount:
                raise HTTPException(
                    status_code=404, detail=f"User not found for email : {email}"
                )
            await self._session.commit()

        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )
