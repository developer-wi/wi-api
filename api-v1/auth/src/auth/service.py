import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import concurrent.futures

from auth.repo import RepoAuth
from auth.scheme import AuthCreate
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
        auth = await self._repo.find_by_id(auth_id)
        return auth

    async def get_auth_by_email(self, auth_email: str):
        """이메일로 사용자 가져오기."""
        auth = await self._repo.find_by_email(auth_email)
        return auth

    async def create_auth(self, auth: AuthCreate):
        """새로운 사용자 생성."""
        hashed_password = await get_password_hash(auth.password, self.thread_pool)
        generated_uuid = str(uuid.uuid1())
        return await self._repo.create(
            name=auth.name,
            uuid=generated_uuid,
            email=auth.email,
            key=hashed_password,
        )

    async def verify_auth(self, email: str, auth_password: str):
        """사용자 인증 및 토큰 생성."""
        auth = await self._repo.find_by_email(email)

        is_verified = await verify_password(auth_password, auth.key, self.thread_pool)
        if not is_verified:
            raise HTTPException(status_code=409, detail="Wrong Password")

        token = await create_token(auth.id, self.thread_pool)
        return {"token": token}

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

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # async def create_token(self, auth_id: int) -> str:
    #     """사용자를 위한 JWT 토큰 생성."""
    #     loop = asyncio.get_running_loop()
    #     return await loop.run_in_executor(self.thread_pool, self._create_token, auth_id)
    #
    # def _create_token(self, auth_id: int):
    #     return jwt.encode({"auth_id": auth_id}, "gPdudtkgkd", algorithm="HS256")

    def shutdown(self):
        self.thread_pool.shutdown(wait=True)
