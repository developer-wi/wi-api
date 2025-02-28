import asyncio
import jwt
from concurrent.futures import ThreadPoolExecutor


async def create_token(user_id: int, thread_pool: ThreadPoolExecutor):
    """사용자를 위한 JWT 토큰 생성."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, _create_token, user_id)


def _create_token(user_id: int):
    return jwt.encode({"user_id": user_id}, "gPdudtkgkd", algorithm="HS256")