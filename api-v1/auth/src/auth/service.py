import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import concurrent.futures

from auth.repo import RepoUser
from auth.scheme import UserCreate
from auth.crypt.util import get_password_hash, verify_password, create_token


class UserService:
    thread_pool: concurrent.futures.ThreadPoolExecutor = (
        concurrent.futures.ThreadPoolExecutor(max_workers=5)
    )

    def __init__(self, db: AsyncSession):
        self._repo = RepoUser(db)

    async def get_user(self, user_id: int):
        """ID로 사용자 가져오기."""
        user = await self._repo.find_by_id(user_id)
        return user

    async def get_user_by_email(self, user_email: str):
        """이메일로 사용자 가져오기."""
        user = await self._repo.find_by_email(user_email)
        return user

    async def create_user(self, user: UserCreate):
        """새로운 사용자 생성."""
        hashed_password = await get_password_hash(user.password, self.thread_pool)
        generated_uuid = str(uuid.uuid1())
        return await self._repo.create(
            name=user.name,
            uuid=generated_uuid,
            email=user.email,
            key=hashed_password,
        )

    async def verify_user(self, email: str, user_password: str):
        """사용자 인증 및 토큰 생성."""
        user = await self._repo.find_by_email(email)

        is_verified = await verify_password(user_password, user.key, self.thread_pool)
        if not is_verified:
            raise HTTPException(status_code=409, detail="Wrong Password")

        token = await create_token(user.id, self.thread_pool)
        return {"token": token}

    async def change_password(self, email: str, password: str, new_password: str):
        """사용자 비밀번호 변경."""
        try:
            user = await self._repo.find_by_email(email)

            is_verified = await verify_password(password, user.key, self.thread_pool)
            if not is_verified:
                raise HTTPException(
                    status_code=409, detail="Password verification failed"
                )

            new_key = await get_password_hash(new_password, self.thread_pool)
            await self._repo.update_key_by_email(email=email, new_key=new_key)

            token = await create_token(user.id, self.thread_pool)
            return token

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # async def create_token(self, user_id: int) -> str:
    #     """사용자를 위한 JWT 토큰 생성."""
    #     loop = asyncio.get_running_loop()
    #     return await loop.run_in_executor(self.thread_pool, self._create_token, user_id)
    #
    # def _create_token(self, user_id: int):
    #     return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")

    def shutdown(self):
        self.thread_pool.shutdown(wait=True)
