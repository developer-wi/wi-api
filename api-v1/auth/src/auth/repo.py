from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from auth.model import Auth


class RepoAuth(object):
    def __init__(self, db: AsyncSession):
        self._session = db

    async def create(self, name: str, uuid: str, email: str, key: str):
        new_auth = Auth(name=name, uuid=uuid, email=email, key=key)
        try:
            self._session.add(new_auth)
            await self._session.commit()
            await self._session.refresh(new_auth)
            return new_auth
        except IntegrityError as e:
            await self._session.rollback()
            if "Duplicate entry" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail=f"email already exists: {email}",
                )
            else:
                raise HTTPException(status_code=409, detail="unknown error adding auth")
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def find_by_id(self, auth_id: int):
        auth = await self._session.get(Auth, auth_id)
        if auth is None:
            raise HTTPException(status_code=404, detail="Auth not found")
        return auth

    async def find_by_uuid(self, auth_uuid: str):
        try:
            result = await self._session.execute(
                select(Auth).where(Auth.uuid == auth_uuid)
            )
            auth = result.scalar_one()
            return auth
        except NoResultFound:
            raise HTTPException(
                status_code=404, detail=f"Auth not found for uuid: {auth_uuid}"
            )
        except MultipleResultsFound:
            raise HTTPException(
                status_code=500,
                detail=f"Multiple auths found for uuid: {auth_uuid}",
            )
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def find_by_email(self, email: str):
        try:
            result = await self._session.execute(
                select(Auth).where(Auth.email == email)
            )
            auth = result.scalar_one()
            return auth
        except NoResultFound:
            raise HTTPException(
                status_code=404, detail=f"Auth not found for email: {email}"
            )
        except MultipleResultsFound:
            raise HTTPException(
                status_code=500,
                detail=f"Multiple auths found for email: {email}",
            )
        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )

    async def update_key_by_email(self, email: str, new_key: str):
        try:
            result = await self._session.execute(
                update(Auth).where(Auth.email == email).values(key=new_key)
            )
            if result.rowcount == 0 or not result.rowcount:
                raise HTTPException(
                    status_code=404, detail=f"Auth not found for email : {email}"
                )
            await self._session.commit()

        except Exception as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=500, detail=f"internal server error: {str(e)}"
            )
