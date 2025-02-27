import asyncio
import bcrypt
import jwt
import functools
from concurrent.futures import ThreadPoolExecutor


# get_password_hash, verify_password 함수를 여기서 구현합니다.


async def get_password_hash(password: str, thread_pool: ThreadPoolExecutor):
    """Hashes a password using bcrypt in a thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, _get_password_hash, password)


def _get_password_hash(password: str):
    """Synchronously hashes a password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


async def verify_password(
    password: str, hashed_password: str, thread_pool: ThreadPoolExecutor
) -> bool:
    """Verifies a password against a hashed password using bcrypt in a thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        thread_pool, _verify_password, password, hashed_password
    )


def _verify_password(password: str, hashed_password: str) -> bool:
    """Synchronously verifies a password against a hashed password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


async def create_token(user_id: int, thread_pool: ThreadPoolExecutor):
    """사용자를 위한 JWT 토큰 생성."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, _create_token, user_id)


def _create_token(user_id: int):
    return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")
