import uuid
import datetime
from fastapi import HTTPException
from redis.commands.search.query import Query
from redis_om import Migrator
from sqlalchemy.ext.asyncio import AsyncSession
import concurrent.futures
from redis_om.model import NotFoundError
from auth.repo import RepoAuth
from auth.scheme import AuthCreate
from auth.model import CacheAuth
from util.crypt import get_password_hash, verify_password
from util.token import create_token


class AuthService:
    thread_pool: concurrent.futures.ThreadPoolExecutor = (
        concurrent.futures.ThreadPoolExecutor(max_workers=5)
    )

    def __init__(self, db: AsyncSession):
        self._repo = RepoAuth(db)

    async def get_auth(self, auth_id: int):
        """ID로 사용자 가져오기."""
        try:
            auth = await self._repo.find_by_id(auth_id)
            return auth
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_auth_by_email(self, auth_email: str):
        """이메일로 사용자 가져오기."""
        try:
            auth = await self._repo.find_by_email(auth_email)
            return auth
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_auth(self, auth: AuthCreate):
        """새로운 사용자 생성."""
        try:
            hashed_password = await get_password_hash(auth.password, self.thread_pool)
            generated_uuid = str(uuid.uuid1())
            return await self._repo.create(
                name=auth.name,
                uuid=generated_uuid,
                email=auth.email,
                key=hashed_password,
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_auth(self, email: str, auth_password: str):
        """사용자 인증 및 토큰 생성."""
        try:
            auth = await self._repo.find_by_email(email)
            is_verified = await verify_password(
                auth_password, auth.key, self.thread_pool
            )
            if not is_verified:
                raise HTTPException(status_code=409, detail="Wrong Password")
            token = await create_token(auth.id, self.thread_pool)

            try:
                # Migrator().run()
                auth_caches = CacheAuth.find(CacheAuth.id == str(auth.id)).all()
                for auth_cache in auth_caches:
                    auth_cache.delete(pk=auth_cache.pk)
            except NotFoundError:
                # no cache to delete, so do nothing
                pass
            r = CacheAuth(
                id=str(auth.id),
                uuid=auth.uuid,
                token=token,
                join_at=datetime.datetime.now(),
            )
            # r.db().expire(name=r.key(), time=600)
            r.save()
            r.expire(num_seconds=600)
            return {"token": token}
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def change_password(self, email: str, password: str, new_password: str):
        """사용자 비밀번호 변경."""
        try:
            auth = await self._repo.find_by_email(email)
            is_verified = await verify_password(password, auth.key, self.thread_pool)
            if not is_verified:
                raise HTTPException(
                    status_code=409, detail="Password verification failed"
                )
            new_key = await get_password_hash(new_password, self.thread_pool)
            await self._repo.update_key_by_email(email=email, new_key=new_key)
            token = await create_token(auth.id, self.thread_pool)
            return token
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def shutdown(self):
        self.thread_pool.shutdown(wait=True)
